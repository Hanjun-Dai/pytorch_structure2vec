#ifndef MOL_LIB_H
#define MOL_LIB_H

typedef float Dtype;

extern "C" int Init(const int argc, const char** argv);

extern "C" void* Smiles2Graph(const char* smiles);

extern "C" int NodeFeatDim();

extern "C" int EdgeFeatDim();

extern "C" int NumNodes(void* _g);

extern "C" int NumEdges(void* _g);

extern "C" int* EdgeList(void* _g);

extern "C" int PrepareBatchFeature(const int num_graphs, void** g_list, Dtype* node_input, Dtype* edge_input);

#endif