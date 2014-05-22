import os, sys, glob

RUNNABLE_PATH = 'runnables'
sys.path.append(RUNNABLE_PATH)

class Runner:

    tasklist = [] 
    runnable_list = []

    def __init__(self):
        for runnable_id in glob.glob(RUNNABLE_PATH + '/*.py'):
            runnable_id = os.path.basename(runnable_id)[:-3]
            self.runnable_list.append(runnable_id)

    def runnable(self, runnable_id):
        return getattr(__import__(runnable_id), 'Runnable')

    def info_list(self):
        result = {} 
        for runnable_id in self.runnable_list:
            result[runnable_id] = self.runnable(runnable_id).info()
        return result

    def run(self, runnable_id, dataset, params, output = None):
        if not runnable_id in self.runnable_list:
            return None

        task = self.runnable(runnable_id)(dataset, params)
        task.run(output)
        self.tasklist.append(task)
        return task

if __name__ == "__main__":

    if len(sys.argv) < 1:
        print('%s <runnable> [params]' % sys.argv[0])
        sys.exit(1)

    sys.argv.pop(0)
    getattr(__import__(sys.argv[0]), 'main')()
