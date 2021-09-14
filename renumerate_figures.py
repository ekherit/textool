#!/usr/bin/python3

import re
import os
import sys
import shutil

input_file_name  = ""
output_dir_name = "tmp"


if len(sys.argv) == 1 or len(sys.argv) > 3:
    print("Usage: prepare <input_file> <ouput_dir>")
    exit(1)

if len(sys.argv) > 1:
    input_file_name = sys.argv[1]

if len(sys.argv) > 2:
    output_dir_name = sys.argv[2]

try:
    os.mkdir(output_dir_name)
except FileExistsError:
    print("ERROR: directory", output_dir_name, "exists!")
    exit(2)

output_file_name = output_dir_name+"/" + input_file_name
    



f = open(input_file_name, 'r')

begin_figure = re.compile(r'.*\\begin\{figure\}.*')
end_figure = re.compile(r'.*\\end\{figure\}.*')
include_graphics = re.compile(r'.*\\includegraphics.*\{(.+)\}.*')
caption = re.compile(r'.*\\caption')
label = re.compile(r'.*\\label\{([^}^{]*)\}')
extention=re.compile(r'.+\.(.+)')
is_figure_env=False
is_new_figure=False
figN=0
figure_name = []
unnumerated_figures = [] #keep file names
figure_sub = []
figure_ref_sub = []
graphics_path=""
graphics_path_re = re.compile(r'.*\\graphicspath\{\{([^{}]+)\}\}')

include_graphics2 = re.compile(r'\\includegraphics(\[[^\{\}]+\])?\{([^\}\}]+)\}')

notcomment_re = re.compile(r'(^[^%]*)(%*)?.*$')

for line in f:
    #remove all comments
    m = notcomment_re.match(line)
    line = m.group(1)

    gp = graphics_path_re.match(line)
    if gp:
        graphics_path = gp.group(1)

    if begin_figure.match(line):
        is_figure_env=True
        continue

    if end_figure.match(line) and is_figure_env :
        is_figure_env=False
        continue

    if is_figure_env:
        m = include_graphics.match(line)
        if m:
            name = m.group(1)
            figure_name.append(name)
    else:
        m = include_graphics2.findall(line)
        for item in m:
            unnumerated_figures.append(item[1])

    if len(figure_name)>0:
        m = label.match(line)
        if m:
            ref = m.group(1)
            figN+=1
            new_ref = "fig:fig{:02d}".format(figN)
            figure_ref_sub.append( (ref, new_ref))
            idx=0
            subfigure_suffix=['a','b','c','d','e','f','g','h']
            if len(figure_name)==1:
                subfigure_suffix=['']
            for name in figure_name:
                ext = extention.match(name).group(1)
                new_name = "fig{:02d}{}.{}".format(figN,subfigure_suffix[idx],ext)
                figure_sub.append( (name, new_name) )
                idx+=1
            figure_name =[]


print(figure_sub)
print(figure_ref_sub)

f.close()

def quote(name):
    return "'"+name+"'"

print("graphicspath = ", graphics_path)
print( "Rename  figures: " )
for figs in figure_sub:
    print("  {:40} ->   {:40}".format(quote(figs[0]), quote(figs[1])))

print( "Rename  figure labeles: " )
for refs in figure_ref_sub:
    print("  {:40} ->   {:40}".format(quote(refs[0]), quote(refs[1])))

print("Keep figure names: ")
for name in unnumerated_figures:
    print("     {:40}".format(quote(name)))


#Now do substitutions
f = open(input_file_name, 'r')
of = open(output_file_name, 'w')
for line in f:
    for figs in figure_sub:
        line  = line.replace(figs[0], figs[1])
    for refs in figure_ref_sub:
        line  = line.replace(refs[0], refs[1])
    #print(line,end='')
    of.write(line)

for figs in figure_sub:
    shutil.copy2(graphics_path+figs[0], output_dir_name+"/"+figs[1])

for figs in unnumerated_figures:
    shutil.copy2(graphics_path+figs, output_dir_name+"/"+figs)
