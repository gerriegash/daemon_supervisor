# Daemon Supervisor

Supervises a process so that it is running all the time.

### Prerequisites

You need Python 3.5 or later to run daemon_supervisor.

In Ubuntu, Mint and Debian you can install Python 3 like this:

$ sudo apt-get install python3 python3-pip
For other Linux flavors, macOS and Windows, packages are available at

http://www.python.org/getit/

and it also makes use of external python module `psutil` which is supposed to be installed automatically when you run the script. 

### Running

```
python3 daemon_supervisor.py -c 'PROCESS_COMMAND'
```

Example

```
python3 daemon_supervisor.py -c 'bash -c "sleep 5 && exit 0"'
```

To use help

```
python3 daemon_supervisor.py -h
```

## How it works

* It creates the daemon supervisor which(tries to) keeps a process running all the time.
* If the process is already running, it waits idle for MONITORING_EVENTS_INTERVAL_SECONDS seconds and then checks again.
* If the process needs a restart, it starts the process again and waits for the RESTART_EVENTS_INTERVAL_SECONDS and polls for 
the number of GIVE_UP_ATTEMPTS configured to restart the process.
