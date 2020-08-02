import pandas as pd
import numpy as np
import itertools


def get_angle(data, vertex, point_a, point_b):
    
    "Get the angle between the vectors from vertex to point_a and vertex to point_b where coordinates have standard format or nose_origin_format"
    vertex_points=data[data['part_names']==vertex][['frame_count','x','y']].rename({'x':'x_vertex','y':'y_vertex'},axis=1)
    a_points=data[data['part_names']==point_a][['frame_count','x','y']].rename({'x':'x_a','y':'y_a'},axis=1)
    b_points=data[data['part_names']==point_b][['frame_count','x','y']].rename({'x':'x_b','y':'y_b'},axis=1)
    
    table=vertex_points.merge(a_points,on='frame_count')
    table=table.merge(b_points,on='frame_count')
    
    table['v_to_a_x']= table['x_a']-table['x_vertex']
    table['v_to_a_y']= table['y_a']-table['y_vertex']
    table['v_to_b_x']= table['x_b']-table['x_vertex']
    table['v_to_b_y']= table['y_b']-table['y_vertex']

    table['dot_product']=table['v_to_a_x']*table['v_to_b_x'] + table['v_to_a_y']*table['v_to_b_y']
    table['len_vtoa']=np.sqrt(table['v_to_a_x']**2+table['v_to_a_y']**2)
    table['len_vtob']=np.sqrt(table['v_to_b_x']**2+table['v_to_b_y']**2)
    table['angle'] = np.degrees(np.arccos(table['dot_product']/np.abs(table['len_vtoa']*table['len_vtob'])))
    
    table=table[['angle']]
    table.rename({'angle':'angle_at_{}'.format(vertex)},axis=1)
    
    return table



def get_blocks(_list, drop_blocks=1, include_False_blocks=False):
    "get consecutive blocks, drop (meaning invert) blocks of length 1. Warning: Multiple execution will invert longer blocks"
    _list=list(_list)
    
    #get blocks/sequences of consecutive true/false elements
    block_list = []
    i=0
    for key, iter in itertools.groupby(_list):
        block_length=len(list(iter))
        block_list.append((key, block_length,i))
        i += block_length
    print("1",block_list)
    
    
    if (include_False_blocks==False):
        block_list = [element for element in block_list if element[0]==True]

    return block_list




