import matplotlib.pyplot as plt


def plot_parameter_sensitivity(
    results,
    metric,
    title=None
):
    """
    Plot a performance metric against momentum weight.
    """

    if title is None:
        title = f"{metric} vs Momentum Weight"

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(
        results["Momentum Weight"],
        results[metric],
        marker="o"
    )

    ax.set_title(title)

    ax.set_xlabel("Momentum Weight")

    ax.set_ylabel(metric)

    ax.grid(True)

    plt.show()