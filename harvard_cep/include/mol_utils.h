#ifndef MOL_UTILS_H
#define MOL_UTILS_H

#include "mol_lib.h"
#include <GraphMol/RingInfo.h>
#include <vector>
#include <GraphMol/ROMol.h>
#include <GraphMol/RWMol.h>
#include <GraphMol/Atom.h>
#include <GraphMol/Bond.h>
#include <GraphMol/FileParsers/MolSupplier.h>
#include <GraphMol/SmilesParse/SmilesParse.h>
#include <map>

/*
'C', 'N', 'O', 'S', 'F', 'Si', 'P', 'Cl', 'Br', 'I', 'B', 'Se'*/
const unsigned atom_nums[] = {6, 7, 8, 16, 9, 14, 15, 17, 35, 53, 5, 34};

struct MolFeat
{
	static const int nodefeat_dim = 12 + 8 + 8 + 8 + 1;
	static const int edgefeat_dim = 6;

	static void InitIdxMap();
	
	static void ParseAtomFeat(Dtype* arr, int feat);
	
	static int AtomFeat(const RDKit::Atom* cur_atom);
	
	static int EdgeFeat(const RDKit::Bond* bond);
	
	static void ParseEdgeFeat(Dtype* arr, int feat);
	
	static std::map<unsigned, unsigned> atom_idx_map;
};


struct MolGraph
{

	MolGraph(std::string smiles);

	void GetDegrees();

	inline int node_feat_at(int node_idx)
	{
		return node_feats[node_idx];
	}

	inline int edge_feat_at(int edge_idx)
	{
		return edge_feats[edge_idx];
	}

	std::vector< std::vector<int> > adj_list;
	std::vector< int > edge_pairs, degrees;
	int num_nodes, num_edges;

private:
	std::vector< int > node_feats, edge_feats;
};

#endif