import ctypes
import numpy as np
import os
import sys
import torch

class _mol_lib(object):

    def __init__(self, args):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.lib = ctypes.CDLL('%s/build/dll/libmol.so' % dir_path)

        self.lib.Smiles2Graph.restype = ctypes.c_void_p
        self.lib.PrepareBatchFeature.restype = ctypes.c_int

        self.lib.NodeFeatDim.restype = ctypes.c_int
        self.lib.EdgeFeatDim.restype = ctypes.c_int
        self.lib.NumNodes.restype = ctypes.c_int
        self.lib.NumEdges.restype = ctypes.c_int

        self.lib.EdgeList.restype = ctypes.POINTER(ctypes.c_int)

        if sys.version_info[0] > 2:
            args = [arg.encode() for arg in args]  # str -> bytes for each element in args
        arr = (ctypes.c_char_p * len(args))()
        arr[:] = args
        self.lib.Init(len(args), arr)

        self.num_node_feats = self.lib.NodeFeatDim()
        self.num_edge_feats = self.lib.EdgeFeatDim()

    def PrepareNodeEdgeFeatures(self, molgraph_list):
        c_list = (ctypes.c_void_p * len(molgraph_list))()
        total_num_nodes = 0
        total_num_edges = 0
        for i in range(len(molgraph_list)):
            c_list[i] = molgraph_list[i].handle
            total_num_nodes += molgraph_list[i].num_nodes
            total_num_edges += molgraph_list[i].num_edges

        torch_node_feat = torch.zeros(total_num_nodes, self.num_node_feats)
        torch_edge_feat = torch.zeros(total_num_edges * 2, self.num_edge_feats)

        node_feat = torch_node_feat.numpy()
        edge_feat = torch_edge_feat.numpy()
        
        self.lib.PrepareBatchFeature(len(molgraph_list), ctypes.cast(c_list, ctypes.c_void_p),
                                    node_feat.ctypes.data, edge_feat.ctypes.data)

        return torch_node_feat, torch_edge_feat

    # def __CtypeNetworkX(self, g):
    #     edges = g.edges()
    #     e_list_from = (ctypes.c_int * len(edges))()
    #     e_list_to = (ctypes.c_int * len(edges))()

    #     if len(edges):
    #         a, b = zip(*edges)
    #         e_list_from[:] = a
    #         e_list_to[:] = b

    #     return (len(g.nodes()), len(edges), ctypes.cast(e_list_from, ctypes.c_void_p), ctypes.cast(e_list_to, ctypes.c_void_p))

    # def TakeSnapshot(self):
    #     self.lib.UpdateSnapshot()

    # def ClearTrainGraphs(self):
    #     self.ngraph_train = 0
    #     self.lib.ClearTrainGraphs()

    # def InsertGraph(self, g, is_test):
    #     n_nodes, n_edges, e_froms, e_tos = self.__CtypeNetworkX(g)
    #     if is_test:
    #         t = self.ngraph_test
    #         self.ngraph_test += 1
    #     else:
    #         t = self.ngraph_train
    #         self.ngraph_train += 1

    #     self.lib.InsertGraph(is_test, t, n_nodes, n_edges, e_froms, e_tos)

    # def LoadModel(self, path_to_model):
    #     p = ctypes.cast(path_to_model, ctypes.c_char_p)
    #     self.lib.LoadModel(p)

    # def GetSol(self, gid, maxn):
    #     sol = (ctypes.c_int * (maxn + 10))()
    #     val = self.lib.GetSol(gid, sol)
    #     return val, sol

dll_path = '%s/build/dll/libmol.so' % os.path.dirname(os.path.realpath(__file__))
if os.path.exists(dll_path):
    MOLLIB = _mol_lib(sys.argv)

    class MolGraph(object):

        def __init__(self, smiles, pce):
            self.smiles = smiles
            p = ctypes.cast(smiles, ctypes.c_char_p)
            self.handle = MOLLIB.lib.Smiles2Graph(p)            
            self.num_nodes = MOLLIB.lib.NumNodes(self.handle)
            self.num_edges = MOLLIB.lib.NumEdges(self.handle)
            self.edge_pairs = np.ctypeslib.as_array(MOLLIB.lib.EdgeList(self.handle), shape=( self.num_edges * 2, ))
            self.pce = pce
else:
    MOLLIB = None
    MolGraph = None

if __name__ == '__main__':

    g = MolGraph('c1ccccc1', 0)
    node_feat, edge_feat = MOLLIB.PrepareNodeEdgeFeatures([g])
    