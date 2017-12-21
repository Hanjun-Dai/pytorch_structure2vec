#include "mol_lib.h"
#include "mol_utils.h"

#include <random>
#include <algorithm>
#include <cstdlib>
#include <signal.h>

int Init(const int argc, const char** argv)
{
    MolFeat::InitIdxMap();
    return 0;
}

int NodeFeatDim()
{
    return MolFeat::nodefeat_dim;
}

int EdgeFeatDim()
{
    return MolFeat::edgefeat_dim;
}

int NumNodes(void* _g)
{
    MolGraph* g = static_cast<MolGraph*>(_g);
    return g->num_nodes;
}

int NumEdges(void* _g)
{
    MolGraph* g = static_cast<MolGraph*>(_g);
    return g->num_edges;
}

void* Smiles2Graph(const char* smiles)
{
    auto* g = new MolGraph(smiles);
    return g;
}

int* EdgeList(void* _g)
{
    MolGraph* g = static_cast<MolGraph*>(_g);
    return g->edge_pairs.data();
}

int PrepareBatchFeature(const int num_graphs, void** g_list, Dtype* node_input, Dtype* edge_input)
{    
    unsigned edge_cnt = 0, node_cnt = 0;
    std::vector< MolGraph* > graph_list(num_graphs);
    
    for (int i = 0; i < num_graphs; ++i)
    {
        MolGraph* g = static_cast<MolGraph*>(g_list[i]);
		node_cnt += g->num_nodes;
		edge_cnt += g->num_edges;
        graph_list[i] = g;
    }
    
    Dtype* ptr = node_input;
    for (int i = 0; i < num_graphs; ++i)
    {
        auto* g = graph_list[i];

		for (int j = 0; j < g->num_nodes; ++j)
		{
			MolFeat::ParseAtomFeat(ptr, g->node_feat_at(j));
			ptr += MolFeat::nodefeat_dim;
		}
    }

	ptr = edge_input;
	for (int i = 0; i < num_graphs; ++i)
	{
		auto* g = graph_list[i];
		for (int j = 0; j < g->num_edges * 2; j += 2)
		{
			// two directions have the same feature
			MolFeat::ParseEdgeFeat(ptr, g->edge_feat_at(j / 2));
			ptr += MolFeat::edgefeat_dim;
			MolFeat::ParseEdgeFeat(ptr, g->edge_feat_at(j / 2));
			ptr += MolFeat::edgefeat_dim;
		}
	}

    return 0;
}