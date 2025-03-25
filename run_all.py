import multiprocessing
from algo.App import app as algoApp
from sim.DashApp import app as statApp
from sim.ui.main import main as Main

def run_algoApp():
    algoApp.run(debug=True, host="127.0.0.1", port=8080, use_reloader=False)

def run_statApp():
    statApp.run(debug=True, host="127.0.0.1", port=80, use_reloader=False)

def main():
    # Start both Flask apps in separate processes
    algo_process = multiprocessing.Process(target=run_algoApp)
    stat_process = multiprocessing.Process(target=run_statApp)

    algo_process.start()
    stat_process.start()

    # Run the main UI function
    Main()

if __name__ == '__main__':
    main()
