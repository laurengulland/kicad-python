# pcbnew_easy.py
# Wrapper API for more convenient/pythonic creation of PCB boards and modules.
# Probably this should better be integrated in the default API instead of as
# a wrapper. However this was the quickest way to improve the usability for
# myself.
#
# All values are in mm, and coordinates and sizes can be given as iterables
# (tuples, lists, numpy arrays, ...)
#
#  Copyright 2014 Piers Titus van der Torren <pierstitus@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import math
import cmath

import pcbnew

# helper functions
def mm(val):
    """Convert mm to internal units"""
    return pcbnew.FromMM(float(val))

def p_mm(x, y):
    """Convert coordinate in mm to internal coordinate"""
    return pcbnew.wxPointMM(float(x), float(y))

def size_mm(x, y):
    """Convert size in mm to internal size"""
    return pcbnew.wxSizeMM(float(x), float(y))

def rotate(coord, angle):
    """Rotate coordinate around (0,0)"""
    coord = (coord[0]+coord[1]*1j) * cmath.exp(math.radians(angle)*1j)
    return (coord.real, coord.imag)

# put all layer definitions in a dict
layer_dict = {'F_Adhes':pcbnew.F_Adhes, 'F_CrtYd':pcbnew.F_CrtYd,
              'F_Cu':pcbnew.F_Cu, 'F_Fab':pcbnew.F_Fab, 'F_Mask':pcbnew.F_Mask,
              'F_Paste':pcbnew.F_Paste, 'F_SilkS':pcbnew.F_SilkS,
              'B_Adhes':pcbnew.B_Adhes, 'B_CrtYd':pcbnew.B_CrtYd,
              'B_Cu':pcbnew.B_Cu, 'B_Fab':pcbnew.B_Fab, 'B_Mask':pcbnew.B_Mask,
              'B_Paste':pcbnew.B_Paste, 'B_SilkS':pcbnew.B_SilkS,
              'Cmts_User':pcbnew.Cmts_User, 'Dwgs_User':pcbnew.Dwgs_User,
              'Eco1_User':pcbnew.Eco1_User, 'Eco2_User':pcbnew.Eco2_User,
              'Edge_Cuts':pcbnew.Edge_Cuts, 'Margin':pcbnew.Margin,
              'In1_Cu':pcbnew.In1_Cu, 'In2_Cu':pcbnew.In2_Cu,
              'In3_Cu':pcbnew.In3_Cu, 'In4_Cu':pcbnew.In4_Cu,
              'In5_Cu':pcbnew.In5_Cu, 'In6_Cu':pcbnew.In6_Cu,
              'In7_Cu':pcbnew.In7_Cu, 'In8_Cu':pcbnew.In8_Cu,
              'In9_Cu':pcbnew.In9_Cu, 'In10_Cu':pcbnew.In10_Cu,
              'In11_Cu':pcbnew.In11_Cu, 'In12_Cu':pcbnew.In12_Cu,
              'In13_Cu':pcbnew.In13_Cu, 'In14_Cu':pcbnew.In14_Cu,
              'In15_Cu':pcbnew.In15_Cu, 'In16_Cu':pcbnew.In16_Cu,
              'In17_Cu':pcbnew.In17_Cu, 'In18_Cu':pcbnew.In18_Cu,
              'In19_Cu':pcbnew.In19_Cu, 'In20_Cu':pcbnew.In20_Cu,
              'In21_Cu':pcbnew.In21_Cu, 'In22_Cu':pcbnew.In22_Cu,
              'In23_Cu':pcbnew.In23_Cu, 'In24_Cu':pcbnew.In24_Cu,
              'In25_Cu':pcbnew.In25_Cu, 'In26_Cu':pcbnew.In26_Cu,
              'In27_Cu':pcbnew.In27_Cu, 'In28_Cu':pcbnew.In28_Cu,
              'In29_Cu':pcbnew.In29_Cu, 'In30_Cu':pcbnew.In30_Cu}

def get_layer(s):
    """Get layer id from layer name

    If it is already an int just return it.
    """
    if isinstance(s, int):
        return s
    return layer_dict[s]

def LayerSet(layers):
    """Create LayerSet used for defining pad layers"""
    bitset = 0
    for l in layers:
        bitset |= 1<<get_layer(l)
    hexset = '{0:013x}'.format(bitset)
    lset = pcbnew.LSET()
    lset.ParseHex(hexset, len(hexset))
    return lset

class Board(object):
    def __init__(self, board=None):
        """Convenience wrapper for pcbnew Board"""
        if board == None:
            # if no board is given create a new board
            board = pcbnew.BOARD()
        self.board = board

    def create_module(self, ref, pos=(0,0)):
        """Create new module on the board"""
        module = pcbnew.MODULE(self.board)
        module.SetReference(ref)
        module.SetPosition(p_mm(pos[0], pos[1]))
        self.board.Add(module)
        return Module(module)

    def copy_module(self, original, ref, pos=(0,0)):
        """Create a copy of an existing module on the board"""
        module = pcbnew.MODULE(self.board)
        module.Copy(original.module)
        module.SetReference(ref)
        module.SetPosition(p_mm(pos[0], pos[1]))
        self.board.Add(module)
        return Module(module)

    def add_track_segment(self, start, end, layer='F_Cu', width=None):
        """Create a track segment"""
        if width == None:
            width = self.board.GetDesignSettings().GetCurrentTrackWidth()
        else:
            width = mm(width)
        t = pcbnew.TRACK(self.board)
        t.SetWidth(width)
        t.SetLayer(get_layer(layer))
        t.SetStart(p_mm(start[0], start[1]))
        t.SetEnd(p_mm(end[0], end[1]))
        self.board.Add(t)
        return t

    def add_track(self, coords, layer='F_Cu', width=None):
        """Create a track polyline

        Create track segments from each coordinate to the next"""
        for n in range(len(coords)-1):
            self.add_track_segment(coords[n], coords[n+1], layer=layer, width=width)

    def add_track_via(self, coord, layer_pair=('B_Cu', 'F_Cu'), size=None, drill=None):
        """Create a via on the board

        Args:
            coord: Position of the via
            layer_pair: Tuple of the connected layers (for example ('B_Cu', 'F_Cu'))
            size: size of via in mm, or None for current selection
            drill: size of drill in mm, or None for current selection
        """
        if size == None:
            size = self.board.GetDesignSettings().GetCurrentViaSize()
        else:
            size = mm(size)
        if drill == None:
            drill = self.board.GetDesignSettings().GetCurrentViaDrill()
        else:
            drill = mm(drill)
        via = pcbnew.VIA(self.board)
        #via.SetFlags( IS_NEW )
        #via.SetViaType( GetDesignSettings().m_CurrentViaType )
        via.SetWidth(size)
        #via.SetNetCode( GetBoard()->GetHighLightNetCode() )
        via.SetEnd(p_mm(coord[0], coord[1]))
        via.SetStart(p_mm(coord[0], coord[1]))

        via.SetLayerPair(get_layer(layer_pair[0]), get_layer(layer_pair[1]))
        via.SetDrill(drill)
        self.board.Add(via)
        return via

    def add_line(self, start, end, layer='F_SilkS', width=0.15):
        """Create a graphic line on the board"""
        a = pcbnew.DRAWSEGMENT(self.board)
        a.SetShape(pcbnew.S_SEGMENT)
        a.SetStart(p_mm(start[0], start[1]))
        a.SetEnd(p_mm(end[0], end[1]))
        a.SetLayer(get_layer(layer))
        a.SetWidth(mm(width))
        self.board.Add(a)
        return a

    def add_polyline(self, coords, layer='F_SilkS', width=0.15):
        """Create a graphic polyline on the board"""
        for n in range(len(coords)-1):
            self.add_line(coords[n], coords[n+1], layer=layer, width=width)

    def add_circle(self, center, radius, layer='F_SilkS', width=0.15):
        """Create a graphic circle on the board"""
        a = pcbnew.DRAWSEGMENT(self.board)
        a.SetShape(pcbnew.S_CIRCLE)
        a.SetCenter(p_mm(center[0], center[1]))
        start_coord = p_mm(center[0], center[1]+radius)
        a.SetArcStart(start_coord)
        a.SetLayer(get_layer(layer))
        a.SetWidth(mm(width))
        a.SetLocalCoord()
        self.board.Add(a)
        return a

    def add_arc(self, center, radius, start_angle, stop_angle, layer='F_SilkS', width=0.15):
        """Create a graphic arc on the board"""
        start_coord = radius * cmath.exp(math.radians(start_angle)*1j)
        start_coord = p_mm(start_coord.real, start_coord.imag)
        angle = stop_angle - start_angle
        a = pcbnew.DRAWSEGMENT(self.board)
        a.SetShape(pcbnew.S_ARC)
        a.SetCenter(p_mm(center[0], center[1]))
        a.SetArcStart(start_coord)
        a.SetAngle(angle*10)
        a.SetLayer(get_layer(layer))
        a.SetWidth(mm(width))
        a.SetLocalCoord()
        self.board.Add(a)
        return a


class Module(object):
    def __init__(self, module):
        """Convenience wrapper for pcbnew Module"""
        self.module = module

    def move(self, pos):
        """Move module to new position on board"""
        self.module.SetPosition(p_mm(pos[0], pos[1]))

    def add_line(self, start, end, layer='F_SilkS', width=0.15):
        """Create a graphic line on the module"""
        a = pcbnew.EDGE_MODULE(self.module)
        a.SetShape(pcbnew.S_SEGMENT)
        a.SetStart(p_mm(start[0], start[1]))
        a.SetEnd(p_mm(end[0], end[1]))
        a.SetLayer(get_layer(layer))
        a.SetWidth(mm(width))
        a.SetLocalCoord()
        self.module.Add(a)
        return a

    def add_polyline(self, coords, layer='F_SilkS', width=0.15):
        """Create a graphic polyline on the module"""
        for n in range(len(coords)-1):
            self.add_line(coords[n], coords[n+1], layer=layer, width=width)

    def add_circle(self, center, radius, layer='F_SilkS', width=0.15):
        """Create a graphic circle on the module"""
        a = pcbnew.EDGE_MODULE(self.module)
        a.SetShape(pcbnew.S_CIRCLE)
        a.SetCenter(p_mm(center[0], center[1]))
        start_coord = p_mm(center[0], center[1]+radius)
        a.SetArcStart(start_coord)
        a.SetLayer(get_layer(layer))
        a.SetWidth(mm(width))
        a.SetLocalCoord()
        self.module.Add(a)
        return a

    def add_arc(self, center, radius, start_angle, stop_angle, layer='F_SilkS', width=0.15):
        """Create a graphic arc on the module"""
        start_coord = radius * cmath.exp(math.radians(start_angle)*1j)
        start_coord = p_mm(start_coord.real, start_coord.imag)
        angle = stop_angle - start_angle
        a = pcbnew.EDGE_MODULE(self.module)
        a.SetShape(pcbnew.S_ARC)
        a.SetCenter(p_mm(center[0], center[1]))
        a.SetArcStart(start_coord)
        a.SetAngle(angle*10)
        a.SetLayer(get_layer(layer))
        a.SetWidth(mm(width))
        a.SetLocalCoord()
        self.module.Add(a)
        return a

    def add_pad(self, pos, size, name='', pad_type='standard', shape='circle',
                drill=1.0, layers=None):
        """Create a pad on the module

        Args:
            pos: pad position in mm
            size: pad size in mm, value if shape == 'circle', tuple otherwise
            name: pad name/number
            pad_type: One of 'standard', 'smd', 'conn', 'hole_not_plated'
            shape: One of 'circle', 'rect', 'oval', 'trapezoid'
            drill: drill size in mm, single value for round hole, or tuple for oblong hole.
            layers: None for default, or a list of layer definitions (for example: ['F_Cu', 'F_Mask'])
        """
        pad_types = {'standard':pcbnew.PAD_STANDARD,
                     'smd':pcbnew.PAD_SMD,
                     'conn':pcbnew.PAD_CONN,
                     'hole_not_plated':pcbnew.PAD_HOLE_NOT_PLATED}
        shapes = {'circle':pcbnew.PAD_CIRCLE,
                  'rect':pcbnew.PAD_RECT,
                  'oval':pcbnew.PAD_OVAL,
                  'trapezoid':pcbnew.PAD_TRAPEZOID}
        pad_type = pad_types[pad_type]
        shape = shapes[shape]

        pad = pcbnew.D_PAD(self.module)

        if layers == None:
            default_mask = {pcbnew.PAD_STANDARD:pad.StandardMask(),
                            pcbnew.PAD_SMD:pad.SMDMask(),
                            pcbnew.PAD_CONN:pad.ConnSMDMask(),
                            pcbnew.PAD_HOLE_NOT_PLATED:pad.UnplatedHoleMask()}
            layers = default_mask[pad_type]
        else:
            layers = LayerSet(layers)

        pad.SetShape(shape)
        if shape == pcbnew.PAD_CIRCLE:
            pad.SetSize(size_mm(size, size))
        else:
            pad.SetSize(size_mm(size[0], size[1]))
        pad.SetAttribute(pad_type)
        pad.SetLayerSet(layers)
        if pad_type in (pcbnew.PAD_STANDARD, pcbnew.PAD_HOLE_NOT_PLATED):
            if hasattr(drill, '__getitem__'):
                pad.SetDrillShape(pcbnew.PAD_DRILL_OBLONG)
                pad.SetDrillSize(size_mm(drill[0], drill[1]))
            else:
                pad.SetDrillSize(size_mm(drill, drill))
        pad.SetPos(p_mm(pos[0], pos[1]))
        pad.SetPadName(name)
        pad.SetLocalCoord()
        self.module.Add(pad)
        return pad

    def save(self, name, fpid):
        """Save footprint to disk"""
        self.module.SetFPID(fpid)

        try:
            pcbnew.FootprintLibCreate(name)
        except:
            pass # we try to create, but may be it exists already
        pcbnew.FootprintSave(name, self.module)

def get_board():
    """Get the current board"""
    return Board(pcbnew.GetBoard())




def test():
    """Make an example board

    Run in the pcbnew scripting console:
      import pcbnew_easy
      pcbnew_easy.test()
    """
    # get current board
    pcb = get_board()

    # create test module
    m = pcb.create_module('test')
    m.add_arc(center=(0,0), radius=8, start_angle=-180, stop_angle=0, width=0.2)
    m.add_line(start=(-8,0), end=(8,0), width=0.2)
    m.add_pad(pos=(-4,-3), size=2, drill=1)
    m.add_pad(pos=(4,-3), size=2, drill=1, layers=['B_Cu','F_Cu'])
    for n, x in enumerate([-1, -.5, 0, .5, 1]):
        m.add_pad(pos=(x,-4), size=(0.25,1.2), name=n, pad_type='smd', shape='rect')

    # move module to right location
    m.move((30,30))

    # add test track with via
    track1 = [(30,26), (30,50), (60,80)]
    track2 = [(60,80), (80,80)]
    pcb.add_track(track1, layer='F_Cu', width=0.25)
    pcb.add_track_via(track1[-1])
    pcb.add_track(track2, layer='B_Cu')

    # add board edge
    ul = (20,20)
    pcb_size = (100,80)
    edge = [ul,
            (ul[0], ul[1]+pcb_size[1]),
            (ul[0]+pcb_size[0], ul[1]+pcb_size[1]),
            (ul[0]+pcb_size[0], ul[1]), ul]
    pcb.add_polyline(edge, layer='Edge_Cuts')