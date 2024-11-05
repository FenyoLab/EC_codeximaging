import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_dapi_distribution(dapi_channel, save_path):

    # Generate KDE plot
    kde = sns.kdeplot(dapi_channel)
    x_values = kde.get_lines()[0].get_xdata()
    y_values = kde.get_lines()[0].get_ydata()

    # Get mean value at peak
    peak_index = np.argmax(y_values)
    mean_at_peak = x_values[peak_index]

    # Get mean value at half peak
    #max_y = np.max(y_values)
    #half_max_y = max_y / 2
    #index_half_max = np.argmax(y_values > half_max_y)
    #x_half_max = x_values[index_half_max]
    #threshold = int(np.floor(x_half_max))
    threshold = 10

    print("Mean value at the peak of KDE:", mean_at_peak)
    print("Cutoff value for filtering DAPI cells:", threshold)

    # Plot KDE and cutoff
    plt.figure(figsize=(8, 8))
    sns.kdeplot(dapi_channel, color='black', label=f'Mean at Peak: {mean_at_peak:.2f}')
    plt.axvline(x=threshold, color='red', linestyle='--', label=f'Cutoff: {threshold:.2f}')
    plt.xlabel('Mean Value')
    plt.xlim(0, 100)
    plt.ylabel('Density')
    plt.title('DAPI Mean Distribution')
    plt.legend(loc='upper right', fontsize='large')
    # Save the plot
    plt.savefig(os.path.join(save_path, 'dapi_distribution.png'))
    plt.close()

    return threshold

if __name__ == '__main__':
    main()