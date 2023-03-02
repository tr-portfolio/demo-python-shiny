from shiny import App, reactive, render, ui
from hydpy.examples import prepare_full_example_2
from hydpy.core import hydpytools
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


app_ui = ui.page_fluid(

    ui.navset_tab(
        # elements ----
        ui.nav("Modell vorbereiten", ui.h2("Demonstration: Python GUI zur Ansteuerung von HydPy"),
    ui.input_date("lastdate", "Enddatum", value='1997-01-01'),
    ui.input_action_button("prepare", "Modell LahnH vorbereiten"),
    ui.output_text_verbatim("txt"),),
        ui.nav("Zeitreihen",
        ui.output_ui("ui_select"),
    ui.input_action_button("simulate", "Zeitreihe plotten"),
    ui.output_plot("plot"),),
        ui.nav("Gewässernetz",
    ui.output_ui("selection_select"),
    ui.input_action_button("plot_network", "Gewässernetz plotten"),
    ui.output_plot("network"),),
    )


)


def server(input, output, session):

    prepared = reactive.Value(False)

    @output
    @render.text
    @reactive.event(input.prepare)
    def txt():
        global hp, pub, TestIO
        with reactive.isolate():
            hp, pub, TestIO = prepare_full_example_2(lastdate=str(input.lastdate()))
            hp.simulate()
            prepared.set(True)
            out = str("Simulation abgeschlossen")
        return (out)

    @output
    @render.ui
    @reactive.event(prepared, ignore_init=True, ignore_none=True)
    def ui_select():
        return ui.input_select(
            "in_select",
            label=f"Nodes",
            choices=hp.nodes.names,
            selected=None,
        )

    @output
    @render.table
    @reactive.event(input.simulate2)
    def hp_table():
        d = {'nodes': hp.nodes}
        df = pd.DataFrame(data=d)
        return(df)

    @output
    @render.plot(alt="Simulation")
    @reactive.event(input.simulate)
    def plot():
        with reactive.isolate():
            hp.nodes[input.in_select()].plot_allseries()

    @output
    @render.ui
    @reactive.event(prepared, ignore_init=True, ignore_none=True)
    def selection_select():
        return ui.input_select(
            "selection",
            label=f"Selections",
            choices=pub.selections.names,
            selected=None,
        )


    @output
    @render.plot(alt="Netz")
    @reactive.event(input.plot_network)
    def network():
        with reactive.isolate():
            graph = hydpytools.create_directedgraph(pub.selections.complete)
            nx.draw_networkx(graph)



app = App(app_ui, server)
