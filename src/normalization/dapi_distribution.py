import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_dapi_distribution(dapi_channel, dapi_threshold, sample, save_path):

    # Generate KDE plot
    kde = sns.kdeplot(dapi_channel)
    x_values = kde.get_lines()[0].get_xdata()
    y_values = kde.get_lines()[0].get_ydata()

    # Get mean value at peak
    peak_index = np.argmax(y_values)
    mean_at_peak = x_values[peak_index]

    print("Mean value at the peak of KDE:", mean_at_peak)
    print("Cutoff value for filtering DAPI cells:", dapi_threshold)

    # Plot KDE and cutoff
    plt.figure(figsize=(8, 8))
    sns.kdeplot(dapi_channel, color='black', label=f'Mean at Peak: {mean_at_peak:.2f}')
    plt.axvline(x=dapi_threshold, color='red', linestyle='--', label=f'Cutoff: {dapi_threshold}')
    plt.xlabel('Mean Value')
    plt.xlim(0, 100)
    plt.ylabel('Density')
    plt.title(f'{sample}: DAPI Mean Distribution')
    plt.legend(loc='upper right', fontsize='large')
    # Save the plot
    plt.savefig(os.path.join(save_path, f'{sample}_dapi_dist.png'))
    plt.close()

if __name__ == '__main__':
    main()