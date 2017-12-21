from __future__ import print_function

import os
import sys
import numpy as np
import torch
import random
from torch.autograd import Variable
from torch.nn.parameter import Parameter
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from tqdm import tqdm

from s2v_lib import S2VLIB

def glorot_uniform(t):
    if len(t.size()) == 2:
        fan_in, fan_out = t.size()
    elif len(t.size()) == 3:
        # out_ch, in_ch, kernel for Conv 1
        fan_in = t.size()[1] * t.size()[2]
        fan_out = t.size()[0] * t.size()[2]
    else:
        fan_in = np.prod(t.size())
        fan_out = np.prod(t.size())

    limit = np.sqrt(6.0 / (fan_in + fan_out))
    t.uniform_(-limit, limit)

def _param_init(m):
    if isinstance(m, Parameter):
        glorot_uniform(m.data)
    elif isinstance(m, nn.Linear):
        m.bias.data.zero_()
        glorot_uniform(m.weight.data)

def weights_init(m):
    for p in m.modules():
        if isinstance(p, nn.ParameterList):
            for pp in p:
                _param_init(pp)
        else:
            _param_init(p)

class MySpMM(torch.autograd.Function):

    @staticmethod
    def forward(ctx, sp_mat, dense_mat):
        ctx.save_for_backward(sp_mat, dense_mat)

        return torch.mm(sp_mat, dense_mat)

    @staticmethod
    def backward(ctx, grad_output):        
        sp_mat, dense_mat = ctx.saved_variables
        grad_matrix1 = grad_matrix2 = None

        assert not ctx.needs_input_grad[0]
        if ctx.needs_input_grad[1]:
            grad_matrix2 = Variable(torch.mm(sp_mat.data.t(), grad_output.data))
        
        return grad_matrix1, grad_matrix2

def gnn_spmm(sp_mat, dense_mat):
    return MySpMM.apply(sp_mat, dense_mat)

class EmbedMeanField(nn.Module):
    def __init__(self, latent_dim, num_node_feats, num_edge_feats, max_lv = 3):
        super(EmbedMeanField, self).__init__()
        self.latent_dim = latent_dim
        self.max_lv = max_lv

        self.w_n2l = nn.Linear(num_node_feats, latent_dim)
        self.w_e2l = nn.Linear(num_edge_feats, latent_dim)
        self.fp_params = nn.Linear(latent_dim, latent_dim)

        self.conv_params = []
        for i in range(self.max_lv):
            self.conv_params.append( nn.Linear(latent_dim, latent_dim) )
        weights_init(self)

    def forward(self, graph_list, node_feat, edge_feat):        
        n2n_sp, e2n_sp, subg_sp = S2VLIB.PrepareMeanField(graph_list)
        node_feat = Variable(node_feat)
        edge_feat = Variable(edge_feat)
        n2n_sp = Variable(n2n_sp)
        e2n_sp = Variable(e2n_sp)
        subg_sp = Variable(subg_sp)

        h = self.mean_field(node_feat, edge_feat, n2n_sp, e2n_sp, subg_sp)

        return h

    def mean_field(self, node_feat, edge_feat, n2n_sp, e2n_sp, subg_sp):
        input_node_linear = self.w_n2l(node_feat)
        input_edge_linear = self.w_e2l(edge_feat)
        e2npool_input = gnn_spmm(e2n_sp, input_edge_linear)

        input_message = input_node_linear + e2npool_input
        input_potential = F.relu(input_message)

        lv = 0
        cur_message_layer = input_potential
        while lv < self.max_lv:
            n2npool = gnn_spmm(n2n_sp, cur_message_layer)
            node_linear = self.conv_params[lv]( n2npool )
            merged_linear = node_linear + input_message

            cur_message_layer = F.relu(merged_linear)
            lv += 1
        out_linear = self.fp_params(cur_message_layer)
        reluact_fp = F.relu(out_linear)

        y_potential = gnn_spmm(subg_sp, reluact_fp)

        return y_potential
