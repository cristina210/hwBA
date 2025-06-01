import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

''' Questa funzione stampa e traccia diverse statistiche di una simulazione.
    Analizza il flusso delle entità, le prestazioni della coda, l'utilizzo delle risorse
    e il matching paziente-infermiere.'''
def print_and_plot_stat(sim, queue_1, store_1, store_2, store_3, nurse_1, nurse_2, nurse_3):
    print("STATISTICHE")
    print("Entità totali arrivate in totale nel sistema:")
    print(sim.entity_arrived)

    print("Entità perse per balking in coda:")
    queue_1.lost_entities.print_object_data_collection()

    print("Entità perse perché non ci sono sufficienti posti nelle stanze:")
    queue_1.lost_entities_after_queue.print_object_data_collection()

    queue_1.length_of_stay.plot_no_time(title="Tempo di permanenza in coda per ogni entità")
    queue_1.len_queues.plot_in_time(queue_1.capacity_max, title="Lunghezza della coda nel tempo")

    print("Media integrale lunghezza della coda:")
    print(queue_1.len_queues.calculate_integral_mean())

    print("Media integrale dimensione store1")
    print(store_1.dim_store.calculate_integral_mean())

    print("Media integrale dimensione store2")
    print(store_2.dim_store.calculate_integral_mean())

    print("Media integrale dimensione store3")
    print(store_3.dim_store.calculate_integral_mean())

    nurse_1.delta_skill_level.plot_no_time("Differenza (positiva) di skill level tra paziente-infermiere")
    nurse_2.delta_skill_level.plot_no_time("Differenza (positiva) di skill level tra paziente-infermiere")
    nurse_3.delta_skill_level.plot_no_time("Differenza (positiva) di skill level tra paziente-infermiere")

    store_1.dim_store.plot_in_time(store_1.capacity_max, title="Numero di pazienti nella stanza 1 nel tempo")
    store_2.dim_store.plot_in_time(store_2.capacity_max, title="Numero di pazienti nella stanza 2 nel tempo")
    store_3.dim_store.plot_in_time(store_3.capacity_max, title="Numero di pazienti nella stanza 3 nel tempo")
    return 0


''' La funzione "output_analysis_length_of_stay" esegue un'analisi di output sui dati di "tempo di permanenza"
    provenienti da repliche di una simulazione.
    L'obiettivo è calcolare una stima della media del tempo di permanenza
    e il suo intervallo di confidenza, tenendo conto del periodo di "burn-in".'''
def output_analysis_length_of_stay(list_stat_length_of_stay):
    sample_means_after_burnin = []
    for i, lista in enumerate(list_stat_length_of_stay):
        if i == 0:
            n = len(lista)
            t = np.arange(1, len(lista) + 1)

            # Somma cumulata
            cumulative_sum = np.cumsum(lista)

            # Media cumulata 
            cumulative_mean = cumulative_sum / t

            # Plot
            plt.plot(t, cumulative_mean)
            plt.xlabel('t')
            plt.ylabel('Media cumulata')
            plt.title('Andamento della media cumulata nel tempo')
            plt.grid(True)
            plt.show()

        burn_in = 500
        
        # Rimuovere i primi valori
        list_with_burn_in = lista[burn_in:]

        # Si calcola la media campionaria dei valori successivi al burn-in
        sample_mean = np.mean(list_with_burn_in)
        sample_means_after_burnin.append(sample_mean)

    # Calcolo della media campionaria e dell'intervallo di confidenza
    media_complessiva = np.mean(sample_means_after_burnin)
    std_campionaria = np.std(sample_means_after_burnin, ddof=1)
    n_replica = len(sample_means_after_burnin)
    intervallo = stats.t.interval(0.95, df=n_replica - 1,
                                  loc=media_complessiva,
                                  scale=std_campionaria / np.sqrt(n_replica))

    print("Medie campionarie di ogni replica dopo il burn-in:")
    print(sample_means_after_burnin)
    print(f"Media complessiva: {media_complessiva:.4f}")
    print(f"Intervallo di confidenza al {0.95*100:.0f}%: ({intervallo[0]:.4f}, {intervallo[1]:.4f})")

    # Plot istogramma normalizzato + curva normale teorica
    plt.figure(figsize=(8, 5))
    count, bins, _ = plt.hist(sample_means_after_burnin, bins='auto', density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Densità empirica')
    x = np.linspace(min(bins), max(bins), 1000)
    pdf = stats.norm.pdf(x, loc=media_complessiva, scale=std_campionaria)
    plt.plot(x, pdf, 'r--', linewidth=2, label='Normale teorica')
    plt.title("Istogramma normalizzato delle medie post-burn-in")
    plt.xlabel("Media campionaria")
    plt.ylabel("Densità")
    plt.legend()
    plt.grid(True)
    plt.show()
    return media_complessiva, intervallo

