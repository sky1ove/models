# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['set_seed', 'plot_model', 'clean_ipython_hist', 'clean_tb', 'clean_mem']

# %% ../nbs/00_core.ipynb 3
from torchview import draw_graph
from IPython.display import display
import sys,gc,traceback,torch,graphviz,random,numpy as np, fastcore.all as fc
graphviz.set_jupyter_format('png') # to avoid cropping in plot_model

# %% ../nbs/00_core.ipynb 6
def set_seed(seed, deterministic=False):
    torch.use_deterministic_algorithms(deterministic)
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

# %% ../nbs/00_core.ipynb 10
def plot_model(model,input_size,device='cpu',expand_nested=True,**kwargs): # input size is always started with batch size
    display(draw_graph(model, input_size=input_size, device=device,expand_nested=expand_nested, **kwargs).visual_graph)

# %% ../nbs/00_core.ipynb 13
def clean_ipython_hist():
    # Code in this function mainly copied from IPython source
    if not 'get_ipython' in globals(): return
    ip = get_ipython()
    user_ns = ip.user_ns
    ip.displayhook.flush()
    pc = ip.displayhook.prompt_count + 1
    for n in range(1, pc): user_ns.pop('_i'+repr(n),None)
    user_ns.update(dict(_i='',_ii='',_iii=''))
    hm = ip.history_manager
    hm.input_hist_parsed[:] = [''] * pc
    hm.input_hist_raw[:] = [''] * pc
    hm._i = hm._ii = hm._iii = hm._i00 =  ''

# %% ../nbs/00_core.ipynb 14
def clean_tb():
    # h/t Piotr Czapla
    if hasattr(sys, 'last_traceback'):
        traceback.clear_frames(sys.last_traceback)
        delattr(sys, 'last_traceback')
    if hasattr(sys, 'last_type'): delattr(sys, 'last_type')
    if hasattr(sys, 'last_value'): delattr(sys, 'last_value')

# %% ../nbs/00_core.ipynb 15
def clean_mem():
    clean_tb()
    clean_ipython_hist()
    gc.collect()
    torch.cuda.empty_cache()
