#include "mol_utils.h"

void MolFeat::InitIdxMap()
{
	atom_idx_map.clear();
    for (unsigned i = 0; i < sizeof(atom_nums) / sizeof(unsigned); ++i)
        atom_idx_map[atom_nums[i]] = i;
}

int MolFeat::AtomFeat(const RDKit::Atom* cur_atom)
{
    // getIsAromatic
    int feat = cur_atom->getIsAromatic();
    feat = feat << 4;
    // getImplicitValence
    if (cur_atom->getImplicitValence() <= 7)
        feat |= cur_atom->getImplicitValence();
    else	
        feat |= 7;
    feat = feat << 4;
    // getTotalNumHs
    if (cur_atom->getTotalNumHs() <= 7)
        feat |= cur_atom->getTotalNumHs();
    else
        feat |= 7;
    feat = feat << 4;
    // getDegree
    feat |= cur_atom->getDegree();
    feat = feat << 8;
    // atom_idx_map
    unsigned x = cur_atom->getAtomicNum();
    assert(atom_idx_map.count(x));

    feat |= atom_idx_map[x];
        
    return feat;			
}

void MolFeat::ParseAtomFeat(Dtype* arr, int feat)
{
    // atom_idx_map
    int base = 0;
    int t = feat & ((1 << 8) - 1);
    arr[t] = 1.0;
    assert(t >= 0 && t < (int)atom_idx_map.size());
    feat >>= 8;
    base += atom_idx_map.size();

    // getDegree
    int mask = (1 << 4) - 1;
    t = feat & mask;
    arr[base + t] = 1.0;
    feat >>= 4;
    base += 8;

    // getTotalNumHs
    t = feat & mask;
    arr[base + t] = 1.0;
    feat >>= 4;
    base += 8;

    // getImplicitValence
    t = feat & mask;
    arr[base + t] = 1.0;
    feat >>= 4;
    base += 8;

    // getIsAromatic
    if (feat & mask)
        arr[base] = 1.0;
}
	
int MolFeat::EdgeFeat(const RDKit::Bond* bond)
{			
        int t = 0;
        auto bt = bond->getBondType();
        if (bt == RDKit::Bond::SINGLE)
            t = 0;
        if (bt == RDKit::Bond::DOUBLE)
            t = 1;
        if (bt == RDKit::Bond::TRIPLE)
            t = 2;				
        if (bt == RDKit::Bond::AROMATIC)
            t = 3;
                            
        int feat = (bond->getOwningMol().getRingInfo()->numBondRings(bond->getIdx()) != 0);  
        feat = (feat << 8) | bond->getIsConjugated();
        feat = (feat << 8) | t;
        return feat;
}

void MolFeat::ParseEdgeFeat(Dtype* arr, int feat)
{
    int mask = (1 << 8) - 1;
    // getBondType
    arr[feat & mask] = 1.0;
    feat >>= 8;		
    // getIsConjugated
    if (feat & mask)
        arr[4] = 1.0;
    feat >>= 8;		
    // is ring
    if (feat & mask)
        arr[5] = 1.0;
}

std::map<unsigned, unsigned> MolFeat::atom_idx_map;


MolGraph::MolGraph(std::string smiles)
{
    RDKit::ROMol* mol = RDKit::SmilesToMol(smiles);
    num_nodes = mol->getNumAtoms();
    num_edges = mol->getNumBonds();
    
    edge_pairs.resize(num_edges * 2);    
    adj_list.resize(num_nodes);
    for (int i = 0; i < num_nodes; ++i)
        adj_list[i].clear();

    for (int i = 0; i < num_nodes; ++i)
    {
        const RDKit::Atom* cur_atom = mol->getAtomWithIdx(i);
        node_feats.push_back(MolFeat::AtomFeat(cur_atom));
    }

    for (int i = 0; i < num_edges; ++i)
    {
        const RDKit::Bond* bond = mol->getBondWithIdx(i);
        unsigned int x = bond->getBeginAtomIdx();
        unsigned int y = bond->getEndAtomIdx();
        edge_pairs[i * 2] = x;
        edge_pairs[i * 2 + 1] = y;
		adj_list[x].push_back(y);
        adj_list[y].push_back(x);
        
        edge_feats.push_back(MolFeat::EdgeFeat(bond));
    }

    GetDegrees();
}

void MolGraph::GetDegrees()
{
    degrees.resize(num_nodes);
    for (int i = 0; i < num_nodes; ++i)
        degrees[i] = 0;
    for (int i = 0; i < num_edges * 2; i += 2)
    {
        degrees[edge_pairs[i]]++;
        degrees[edge_pairs[i + 1]]++;
    }
}