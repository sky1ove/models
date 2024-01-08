# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_blocks.ipynb.

# %% auto 0
__all__ = ['make_model', 'lin', 'SelfAttn', 'SE', 'Res_SE']

# %% ../nbs/01_blocks.ipynb 3
import math, torch, torch.nn as nn,fastcore.all as fc
from einops import rearrange
from .core import *
from fastcore.all import partial

# %% ../nbs/01_blocks.ipynb 5
def make_model(block_type, units, **kwargs):
    "Build models based on block and units"
    layers = nn.Sequential()
    for i in range(len(units)-1):
        # Use the block_type parameter to dynamically create blocks
        block = block_type(units[i], units[i+1], **kwargs)
        layers.append(block)
    return layers

# %% ../nbs/01_blocks.ipynb 7
def lin(ni, nf, act=nn.SiLU, norm=None,bias=True,dp=None):
    "single linear block"
    layers = nn.Sequential(nn.Linear(ni, nf, bias=bias))
    if norm: layers.append(norm(nf))
    if dp: layers.append(nn.Dropout(dp))
    if act : layers.append(act())
    return layers

# %% ../nbs/01_blocks.ipynb 17
class SelfAttn(nn.Module):
    
    def __init__(self, embedding_dim, nheads):
        super().__init__()

        self.nheads = nheads
        self.attn_chans = embedding_dim//self.nheads
        assert embedding_dim == self.attn_chans*self.nheads, "embedding_dim is not divisible by nheads"

        self.scale = math.sqrt(embedding_dim/self.nheads)
        self.norm = nn.LayerNorm(embedding_dim)
        self.qkv = nn.Linear(embedding_dim, embedding_dim*3)
        self.proj = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, x, mask=None):
        # bs,seq_length,embedding_dim
        b,l,h = x.shape

        x = self.norm(x)
        x = self.qkv(x)
        x = rearrange(x, 'b l (h attn_chans) -> b h l attn_chans', h=self.nheads)

        q,k,v = torch.chunk(x, 3, dim=-1)
        attn = (q@k.transpose(-1,-2))/self.scale
        attn = attn.softmax(dim=-1)

        if mask is not None:
            attn = attn*mask[:,None,None,:]

        x = attn@v
        x = rearrange(x, 'b h l attn_chans -> b l (h attn_chans)', h=self.nheads)
        x = self.proj(x)
        return x

# %% ../nbs/01_blocks.ipynb 30
class SE(nn.Module):
    "Squeeze & Excitation block for image"
    def __init__(self, channel_in, reduction=2):
        super().__init__()
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channel_in, channel_in // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel_in // reduction, channel_in, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        y = self.squeeze(x).squeeze()
        y = self.excitation(y)[:,:,None,None]
        return x * y.expand_as(x)

# %% ../nbs/01_blocks.ipynb 35
class Res_SE(nn.Module):
    "Resnet + SE block"
    def __init__(self, in_c, out_c,kernel_size=7):
        super().__init__()

        if not kernel_size % 2:
            raise ValueError("kernel_size should be an odd number")

        self.conv = nn.Sequential(
            nn.Conv2d(in_c, out_c, kernel_size, padding='same', bias=False),
            nn.BatchNorm2d(out_c),
            SE(out_c),
            nn.GELU())

        self.res = nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=1, bias=False),
                nn.BatchNorm2d(out_c)) if in_c != out_c else fc.noop


    def forward(self, x):
        x = self.res(x) + self.conv(x)
        return x
