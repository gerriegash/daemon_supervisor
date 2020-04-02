from psutil import STATUS_STOPPED,STATUS_ZOMBIE,STATUS_DEAD,Process
import logging
import setup

PROCESS_COMMAND = None
CURRENT_PROCESS = None

def process_needs_restart():
    """Returns the status of process if it needs a restart or not

    :return:
        True or False
    """
    return get_current_process().status() == STATUS_STOPPED or get_current_process().status() == STATUS_ZOMBIE or get_current_process().status() == STATUS_DEAD


def wait(
    time_in_seconds
):
    """Makes the program sleep for certain time period

    :param time_in_seconds:
        Time period in seconds
    """
    from time import sleep
    logging.info("Sleeping for {} seconds".format(time_in_seconds))
    sleep(time_in_seconds)

def restart_the_process(
    give_up_attempts,
    restart_events_interval_seconds
):
    """Restarts the process and in case the process does not restart, it tries again for a no of times before giving up.

    :param give_up_attempts:
        Attempts to restart the process before giving up
    :param restart_events_interval_seconds:
        Waiting time between restarting events
    :return:
        True or False if the service was not able to be restarted between restart_events_interval_seconds for number of give_up_attempts
    """
    no_of_checks_done = 0

    while no_of_checks_done < give_up_attempts and process_needs_restart():

        create_the_process()# Restart the process
        no_of_checks_done = no_of_checks_done + 1# Increment the no_of_checks_done
        logging.info("Waiting after restart of process and trying again if unsuccessful")
        wait(restart_events_interval_seconds)

        logging.debug("no_of_checks_done = {} ".format(no_of_checks_done))
        logging.debug("no_of_attempts_to_give_up = {} ".format(give_up_attempts))
        logging.debug("no_of_checks_done < no_of_attempts_to_give_up = {}".format(no_of_checks_done < give_up_attempts))
        logging.debug("process_needs_restart = {} ".format(process_needs_restart()))

    if no_of_checks_done == give_up_attempts:
        logging.info("Daemon Supervisor gave up after {} attempts on restarting this process".format(give_up_attempts))
        return False
    return True

def keep_the_process_running(
    give_up_attempts,
    restart_events_interval_seconds
):
    """Tries to keep the process running

    :param give_up_attempts:
        Number of times the Supervisor should try restarting the process before giving up
    :param restart_events_interval_seconds:
        Seconds to wait until the Supervisor monitors the process again"
    :return:
        True or False if the program was able to keep the service running
    """

    if process_needs_restart() :
        logging.info("Restart needed for Process {}".format(get_current_process().name))
        return restart_the_process(give_up_attempts, restart_events_interval_seconds)
    else :
        return True

def setup_logging(
    log_events
):
    """Sets up the logging

    :param log_events:
        if events should be logged or not
    """
    logging.basicConfig(level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")
    if not log_events:
        logging.disable()

def create_the_process():
    """Creates a new process from the command provided in arguments and terminates the previous not alive if any

    :return:
        psutils wrapped process object
    """
    from subprocess import Popen
    import shlex

    if not get_current_process() == None: # terminate existing process
        get_current_process().terminate()

    proc = Popen(shlex.split(get_process_command())) # start a new one
    process = Process(proc.pid)
    logging.info("Created a new process {}".format(process.name))
    set_current_process(process)

def get_current_process():
    return CURRENT_PROCESS

def set_current_process(
    process
):
    global CURRENT_PROCESS;
    CURRENT_PROCESS=process

def get_process_command():
    return PROCESS_COMMAND

def set_process_command(
    process
):
    global PROCESS_COMMAND;
    PROCESS_COMMAND = process

def parse_arguments():
    """Parse the arguments through command line

    :return:
        args array
    """
    from argparse import ArgumentParser
    parser = ArgumentParser(description = "Run the Daemon Supervisor")
    parser.add_argument("-c",
                        "--command",
                        type = str,
                        required = True,
                        help = "Command for the process to be monitored")
    parser.add_argument("-mi",
                        "--monitoring-events-interval-seconds",
                        type = int,
                        default = 11,
                        help = "Seconds to wait until the Supervisor monitors the process again")
    parser.add_argument("-ri",
                        "--restart-events-interval-seconds",
                        type = int,
                        default = 10,
                        help = "Seconds to wait until the Supervisor monitors the process again")
    parser.add_argument("-g",
                        "--give-up-attempts",
                        type = int,
                        default = 5,
                        help = "Number of times the Supervisor should try restarting the process before giving up")
    parser.add_argument("-l",
                        "--log-events",
                        type = bool,
                        default = True,
                        help = "Should log events in a separate file(daemon-supervisor.log)")
    args = parser.parse_args()

    set_process_command(args.command)

    return args

def run():
    """Main function"""

    args = parse_arguments()
    setup_logging(args.log_events)
    create_the_process()
    while True:
        restart_successful = keep_the_process_running(args.give_up_attempts, args.restart_events_interval_seconds)
        if restart_successful:
            logging.info("Waiting idle.")
            wait(args.monitoring_events_interval_seconds)

if __name__ == "__main__":
        run()