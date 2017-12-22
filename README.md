# pytorch_structure2vec
pytorch implementation of structure2vec

## Setup

Build the c++ backend of s2v_lib and you are all set.

```
cd s2v_lib
make -j4  
```

## Reproduce Experiments on Harvard Clean Energy Project

First, you need to install rdkit (https://github.com/rdkit/rdkit) from source. Then set RDBASE to your built rdkit.
```
export RDBASE=/path/to/your/rdkit
```

Build the c++ backend of harvard_cep. 

```
cd harvard_cep
make -j4
```

Download data. Put it under the data folder. Here is the data split provided by [Wengong Jin](http://people.csail.mit.edu/wengong/). 

https://drive.google.com/drive/folders/0B0GLTTNiVPEkdmlac2tDSzBFVzg

The test split is also used in our paper (Dai. et.al, ICML 2016). 

### Model dump

The pretrained model is under ```saved/``` folder. 
```
$ python main.py -mode gpu -saved_model saved/mean_field.model -phast test
====== begin of s2v configuration ======
| msg_average = 0
======   end of s2v configuration ======
loading data
train: 1900000
valid: 82601
test: 220289
loading model from saved/epoch-best.model
loading graph from data/test.txt.bin
num_nodes: 6094162	num_edges: 7357400
100%|███████████████████████████████████████████████████████████████████████████████████| 220289/220289 [00:01<00:00, 130103.34it/s]
mae: 0.08846 rmse: 0.11290: 100%|███████████████████████████████████████████████████████████| 4406/4406 [00:15<00:00, 279.01batch/s]
average test loss: mae 0.07017 rmse 0.09724
```

#### Reference

```bibtex
@article{dai2016discriminative,
  title={Discriminative Embeddings of Latent Variable Models for Structured Data},
  author={Dai, Hanjun and Dai, Bo and Song, Le},
  journal={arXiv preprint arXiv:1603.05629},
  year={2016}
}
```
