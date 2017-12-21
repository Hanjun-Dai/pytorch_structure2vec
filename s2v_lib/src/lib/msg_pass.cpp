#include "msg_pass.h"

void n2n_construct(GraphStruct* graph, long long* idxes, Dtype* vals)
{
    int nnz = 0;    
    long long* row_ptr = idxes;
    long long* col_ptr = idxes + graph->num_edges;

	for (uint i = 0; i < graph->num_nodes; ++i)
	{
		auto& list = graph->in_edges->head[i];
		for (size_t j = 0; j < list.size(); ++j)
		{            
            vals[nnz] = cfg::msg_average ? 1.0 / list.size() : 1.0;
            row_ptr[nnz] = i;
			col_ptr[nnz] = list[j].second;
			nnz++;
		}
	}
	assert(nnz == (int)graph->num_edges);
}

void e2n_construct(GraphStruct* graph, long long* idxes, Dtype* vals)
{
    int nnz = 0;
    long long* row_ptr = idxes;
    long long* col_ptr = idxes + graph->num_edges;

	for (uint i = 0; i < graph->num_nodes; ++i)
	{
		auto& list = graph->in_edges->head[i];
		for (size_t j = 0; j < list.size(); ++j)
		{
			vals[nnz] = cfg::msg_average ? 1.0 / list.size() : 1.0;
			row_ptr[nnz] = i;
			col_ptr[nnz] = list[j].first;
			nnz++;			
		}
	}
	assert(nnz == (int)graph->num_edges);
}

void subg_construct(GraphStruct* graph, long long* idxes, Dtype* vals)
{
    int nnz = 0;    
    long long* row_ptr = idxes;
	long long* col_ptr = idxes + graph->num_nodes;

	for (uint i = 0; i < graph->num_subgraph; ++i)
	{
		auto& list = graph->subgraph->head[i];
		for (size_t j = 0; j < list.size(); ++j)
		{
			vals[nnz] = cfg::msg_average ? 1.0 / list.size() : 1.0;
			row_ptr[nnz] = i;
			col_ptr[nnz] = list[j];
			nnz++;
		}
	}	
	assert(nnz == (int)graph->num_nodes);	
}