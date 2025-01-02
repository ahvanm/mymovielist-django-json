import pandas as pd
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import kneed
from .models import ListEntry

class KMeansCluster:
    def __init__(self, user_id: int, output_folder: str):
        self.df = pd.DataFrame(list(ListEntry.objects.filter(user_id=user_id).values()))
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    def _open_file_write(self, extension: str):
        return open(''.join((self.output_folder, f'/{extension}')), 'w')

    def df_summary_stats(self) -> None:
        df = self.df
        f = self._open_file_write('q1.1_summary_stats.txt')
        f.write('SUMMARY STATISTICS:\n\n')
        f.write(df.describe(include='all').to_string() + '\n\n')
        f.write('DATA TYPES:\n\n')
        f.write(df.dtypes.to_string() + '\n\n')
        f.write('N/A DATA POINTS:\n\n')
        f.write(df.isna().sum().to_string())

    def clean_normalize_df(self) -> None:
        self.df = self.df.dropna()

        for col in self.df.columns:
            mean = self.df[col].mean()
            std = self.df[col].std()
            if std == 0:
                std = 1e-7

            self.df[col] = (self.df[col] - mean) / std

    def euclidean_distance(self, x1: np.ndarray, x2: np.ndarray, axis=-1):
        if axis == -1:
            return np.linalg.norm(x1 - x2)
        return np.linalg.norm(x1 - x2, axis=axis)

    def kmeans_epoch(self, X, k, max_iters=100):
        X_numpy = X.to_numpy()
        centroids = X.sample(k, random_state=42).to_numpy()
        labels = []

        for _ in range(max_iters):
            labels = np.array([np.argmin([self.euclidean_distance(x, cen) for cen in centroids]) for x in X_numpy])
            new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(k)])

            if np.all(centroids == new_centroids):
                break

            centroids = new_centroids

        return centroids, labels

    def silhouette_score(self, X, labels):
        example_count = X.shape[0]
        unique_labels = np.unique(labels)
        cluster_count = len(unique_labels)

        if cluster_count < 2 or cluster_count == example_count:
            return 0.0

        silhouette_scores = []
        for i in range(example_count):
            points_in_same_cluster = X[labels == labels[i]]
            ith_example = X[i]

            a = (np.sum(self.euclidean_distance(points_in_same_cluster, ith_example, axis=1)) /
                 (len(points_in_same_cluster) - 1))

            b_values = []
            for j in unique_labels:
                if j != labels[i]:
                    b_values.append(np.mean(self.euclidean_distance(X[labels == j], ith_example, axis=1)))
            b = min(b_values)

            silhouette_scores.append((b - a) / max(a, b))

        return np.mean(silhouette_scores)

    def wcss(self, X, labels, centroids):
        return sum(self.euclidean_distance(x, centroids[label]) ** 2 for x, label in zip(X, labels))

    def plot_sil(self, sil_avgs, k_values):
        plt.figure()
        plt.plot(k_values, sil_avgs, marker='o')
        plt.xlabel("Number of clusters (k)")
        plt.ylabel("Average Silhouette Score")
        plt.title("Silhouette Analysis")
        plt.savefig(''.join((self.output_folder, f'/q2.2_silhouette_avgs_plot.png')))

    def plot_wcss(self, wcss_vals, k_values):
        plt.figure()
        plt.plot(k_values, wcss_vals, marker='o')
        plt.xlabel('Number of clusters (k)')
        plt.ylabel('WCSS Values')
        plt.title('Elbow Method for Optimal k')
        plt.savefig(''.join((self.output_folder, f'/q2.3_wcss_vals_plot.png')))

    def compare_analyses(self, k1, k2):
        f = self._open_file_write('q2.3_compare_analyses.txt')
        if k1 != k2:
            f.write(f'Chosen value of k: {k1}. This comes from the Silhouette score analysis.\n'
                    f'The WCSS analysis resulted in an optimal k value of {k2}. There is a discrepancy because WCSS\n'
                    f'only considers the compactness of each cluster, while the Silhouette score considers both the cluster\'s\n'
                    f'compactness as well as the general distance away from other clusters, so I chose the latter.\n\n')
        else:
            f.write(f'Chosen value of k: {k2}. Both analyses coincidentally resulted in the same optimal k value.\n'
                    f'Usually, there is a discrepancy because WCSS only considers the compactness of each cluster, while the\n'
                    f'Silhouette score considers both the cluster\'s compactness as well as the distance away from other clusters.\n\n')

    def print_cluster_characteristics(self, X, all_labels, actual_k, low_k):
        k = actual_k - low_k
        labels = all_labels[k]
        unique_labels = np.unique(labels)

        f = self._open_file_write('q3_cluster_characteristics.txt')
        f.write(
            f'K value: {actual_k}. Each of the following clusters\' profiles are defined by the features with the most\n'
            f'extreme mean values (smallest or largest mean values) and/or relatively smaller standard deviation\n'
            f'magnitudes. The first cluster consists of houses with slightly below average features (besides latitude\n'
            f'and median age per house), with a relatively average median house value. The second cluster consists of\n'
            f'households with a relatively high number of rooms and bedrooms, relatively lower median of age, higher\n'
            f'population and households in the house block, and slightly higher median house value on average compared to\n'
            f'houses in the other cluster (with respect to the average California household).\n\n')
        for label in unique_labels:
            i_labels = [i for i, l in enumerate(labels) if l == label]
            X_sub = X.iloc[i_labels]
            X_sub_mean = X_sub.mean()
            X_sub_std = X_sub.std()

            f.write(f'CLUSTER #{label}:\n')
            f.write(f'Mean of each feature in this cluster:\n')
            f.write(f'{X_sub_mean}\n')
            f.write(f'St. Dev. of each feature in this cluster:\n')
            f.write(f'{X_sub_std}\n\n')

    def kmeans_clustering(self, X, lower_bound_k, upper_bound_k):
        k_values = range(lower_bound_k, upper_bound_k + 1)
        plt.figure()
        X_numpy = X.to_numpy()
        wcss_vals = []
        sil_avgs = []
        all_centroids = []
        all_labels = []

        for k in k_values:
            centroids, labels = self.kmeans_epoch(X, k)
            all_centroids.append(centroids)
            all_labels.append(labels)
            print(f'Completed kmeans with k = {k}')

            sil_avgs.append(self.silhouette_score(X_numpy, labels))
            print(f'Added silhouette avg')

            wcss_vals.append(self.wcss(X_numpy, labels, centroids))
            print(f'Added wcss val')

        self.plot_sil(sil_avgs, k_values)
        opt_k1 = np.argmax(sil_avgs) + lower_bound_k
        print('Silhouette result: ', opt_k1)

        self.plot_wcss(wcss_vals, k_values)
        opt_k2 = kneed.knee_locator.KneeLocator(k_values, wcss_vals, curve='convex', direction='decreasing').knee
        print('WCSS result: ', opt_k2)

        self.compare_analyses(opt_k1, opt_k2)
        self.print_cluster_characteristics(X, all_labels, opt_k1, lower_bound_k)


# if __name__ == "__main__":
#     c = KMeansCluster(sys.argv[1], sys.argv[2])
#     c.df_summary_stats()
#     c.clean_normalize_df()
#     c.kmeans_clustering(c.df, 2, 7)
