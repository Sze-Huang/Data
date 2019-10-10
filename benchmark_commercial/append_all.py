import glob, os, sys
import pandas as pd
import argparse
import numpy as np

### Folder contain csv
import argparse 
parser = argparse.ArgumentParser(description="Process initial benchmark results by circuits and combine all the results into new files in /data/new/all_withNegSlack.csv")
parser.add_argument("-d", "--dir", dest="path", required=True, help="Directory which contains original benchmark results")
parser.add_argument("-x", "--exclude", dest="exclude", required=False, action = 'store_true', help="Exclude benchmark")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

args = parser.parse_args()

path = args.path

try:
    checkpath = os.path.abspath(path)
    os.stat(path)
except OSError:
    print ("Directory '{}' does not exists.".format(path))
    sys.exit(2)
print ("Current directory : ", path)

# path = "/home/roy/py/WORK/Untitled Folder/Benchmark Folder"
benchmarkInfo = pd.read_csv("{}/benchmarkInfo.csv".format(path))
libraryName = pd.read_csv("{}/Library_name.csv".format(path))

def all_data():
    all_data = pd.DataFrame()
    for file in glob.glob(path + '/AI_results*.csv'):
        df = pd.read_csv(file, header = 0)
        # df.info()

        s = os.path.basename(file)
        start = 'AI_results_s' #change according to file name
        end = '_bench.csv' #change according to file name
        benchmarkname =  s[s.find(start)+len(start):s.rfind(end)]
        # print (benchmarkname)

        d_value = benchmarkInfo.query('Circuit_Name=={}'.format(benchmarkname))['D-type_flipflops'].iloc[0]
        aon_value = benchmarkInfo.query('Circuit_Name=={}'.format(benchmarkname))['ANDORNOT_Gates'].iloc[0]
        t_value = benchmarkInfo.query('Circuit_Name=={}'.format(benchmarkname))['Total_Gates'].iloc[0]
        # print (d_value, aon_value, t_value
        df.insert(4, 'd_flipflop', d_value)
        df.insert(5, 'aon_gates', aon_value)
        df.insert(6, "total_gates", t_value)
        
        library = []
        for index, row in df.iterrows():
            library.append(libraryName.query("Track == '{}' and Voltage == '{}'".format(row['Track'], row['Voltage']))['Library'].item())
        df['library'] = library
        df['benchmark_name'] = benchmarkname
        df['Total Power'] = df['Dynamic Power'] + df['Leakage Power']
        
        df = df[['Track', 'Voltage', 'Frequency', 'd_flipflop', 'aon_gates', 'Leaf Cell', 'Total Power', 'Worst Slack', 'Cell Area', 'library', 'benchmark_name', 'Dynamic Power', 'Leakage Power']]


        all_data = all_data.append(df, ignore_index = True)
        print ('Done {} file'.format(benchmarkname))
    all_data.to_csv ('{}/all.csv'.format(path), index=False) 

def exclude():
    try:
        checkpath = os.path.abspath('{}/all.csv'.format(path))
        os.stat(checkpath)
    except OSError:
        print ("File '{}' does not exists.".format(path + '/all.csv'))
        sys.exit(2)

    df = pd.read_csv(path + '/all.csv', header = 0)
    benchmark = df.benchmark_name.unique()
    for name in benchmark:
        df_ex = df.query('benchmark_name!={}'.format(name))
        df_ex.to_csv ('{}/allx{}.csv'.format(path, name), index=False) 
        print ('Done {} file'.format(name))


if args.exclude is True:
    exclude()
else:
    all_data()