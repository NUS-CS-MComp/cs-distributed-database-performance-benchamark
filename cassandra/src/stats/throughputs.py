import pandas as pd
import numpy as np
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('input filename not specified')
    input_file = sys.argv[1]
    df = pd.read_csv(input_file, names=['exp_no', 'cli_no', 'a', 'b', 'c', 'd', 'e', 'f', 'g'])
    avg_th = df.groupby('exp_no')['c'].mean().to_numpy()
    min_th = df.groupby('exp_no')['c'].min().to_numpy()
    max_th = df.groupby('exp_no')['c'].max().to_numpy()
    result = np.column_stack([min_th, avg_th, max_th])
    result_df = pd.DataFrame(result, index=np.arange(1, 5))
    result_df.to_csv('throughput.csv', header=False)
