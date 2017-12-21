import sys
import os
from mol_lib import MOLLIB, MolGraph
import torch
import random
import numpy as np
sys.path.append('%s/../s2v_lib' % os.path.dirname(os.path.realpath(__file__)))
from embedding import EmbedMeanField

import argparse

cmd_opt = argparse.ArgumentParser(description='Argparser for harvard cep')
cmd_opt.add_argument('-saved_model', default=None, help='start from existing model')
cmd_opt.add_argument('-batch_size', type=int, default=200, help='minibatch size')
cmd_opt.add_argument('-seed', type=int, default=1, help='seed')
cmd_opt.add_argument('-gen_depth', type=int, default=10, help='depth of generator')
cmd_opt.add_argument('-num_epochs', type=int, default=1000, help='number of epochs')
cmd_opt.add_argument('-latent_dim', type=int, default=16, help='dimension of latent layers')
cmd_opt.add_argument('-max_lv', type=int, default=3, help='max rounds of message passing')
cmd_opt.add_argument('-learning_rate', type=float, default=0.001, help='init learning_rate')

cmd_args, _ = cmd_opt.parse_known_args()

def load_data():
    raw_data_dict = {}
    for fname in ['train', 'valid', 'test']:
        d = []
        with open('./data/%s.txt' % fname, 'r') as f:
            for row in f:
                row = row.split()
                d.append( (row[0].strip(), float(row[1].strip())) )
        raw_data_dict[fname] = d
        print('# %s: %d' % (fname, len(d)))
    return raw_data_dict

def resampling_idxes(d):

if __name__ == '__main__':
    random.seed(cmd_args.seed)
    np.random.seed(cmd_args.seed)
    torch.manual_seed(cmd_args.seed)

    raw_data_dict = load_data()

    # g = MolGraph('c1ccccc1')
    # node_feat, edge_feat = MOLLIB.PrepareNodeEdgeFeatures([g, g])    
    
    # s2v_model = EmbedMeanField(latent_dim=cmd_args.latent_dim, 
    #                             num_node_feats=MOLLIB.num_node_feats, 
    #                             num_edge_feats=MOLLIB.num_edge_feats,
    #                             max_lv=cmd_args.max_lv)

    # embed = s2v_model([g, g], node_feat, edge_feat)

    # print(embed)