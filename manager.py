from loadArff import DataManager

def parse_line_params(line):
  if "-h" in line:
    print "MLSystemManager -L [LearningAlgorithm] -A [ARFF_File] -E [EvaluationMethod] {[ExtraParameters]} [-N] [-R seed]"
    print "Parameters: "
    print "-L [LearningAlgorithm] (required) : specifies the python file which has a class in it named [LearningAlgorithm] which inherits from SupervisedLearner"
    print "-A [ARFF_File] (required) : specifies which file the learning algorithm should work on"
    print "-E [EvaluationMethod] (required) : specifies the evaluation method (see http://axon.cs.byu.edu/~martinez/classes/478/stuff/Toolkit.html)"
    print "-N (optional) : normalize the training and test sets (as provided in the data file)"
    return
  if not set(["-L", "-A", "-E"]).issubset(set(line)):
    if "-L" not in line:
      print "You must provide a learner"
    if "-A" not in line:
      print "you must provide a ARFF file"
    if "-E" not in line:
      print "you must provide a method"
    print "For help try: ./MLSystemManager -h"
    return
  learner = line[line.find("-L")+1]
  if learner[0] == "-":
    print "[LearningAlgorithm] must be a valid python file name"
    print "Got {}".format(learner)
    return
  percent_for_training = None
  num_folds = None
  eval_method = line[line.find("-E")+1]
  if eval_method == "training":
    data_file = line[line.find("-A")+1]
  elif eval_method == "static":
    data_file = (line[line.find("-A")+1], line[line.find("static")+1])
  elif eval_method == "random":
    data_file = line[line.find("-A")+1]
    percent_for_training = int(line[line.find("random")+1])
  elif eval_method == "cross":
    data_file = (line[line.find("-A")+1], line[line.find("static")+1])
    num_folds = int(line[line.find("cross")+1])
  return learner, data_file, eval_method, line.find("-N") != -1, percent_for_training, num_folds

def runner(learner, data_file, eval_method, N=False, train_percent=None, num_folds=None):
  learner_class = getattr(__import__(learner, fromlist=[learner]), learner)
  try:
    if eval_method == "static":
      if not isinstance(data_file, tuple):
        raise ValueError("When using static eval method second file must be included")
      data_manager = DataManager(data_file[0], data_file[1])
    else:
      data_manager = DataManager(data_file)
  except IOError:
    raise ValueError("Couldn't find file '{}'".format(data_file))
  print "Dataset name: {}".format(data_manager.relation_name)
  print "Dataset is{} normalized.".format("" if N else "'nt")
  print "Number of instances: {}".format(data_manager.data.shape[0])
  print "Number of features: {}".format(data_manager.data.shape[1]-1)
  print "Learning algorithm: {}".format(learner_name.replace('.py', ''))
  print "Evaluation method: {}".format(eval_method)
  print
  if eval_method == "training":
    stats = learner_class.measureAccuracy(data_manager.train_data, data_manager.train_labels)
  elif eval_method == "static":
    stats = learner_class.measureAccuracy(data_manager.train_data, data_manager.train_labels)
  elif eval_method == "random":
    data_manager.test_train_split(train_percent)
    stats = learner_class.measureAccuracy(data_manager.train_data, data_manager.train_labels)
  elif eval_method == "cross":
    pass
  else:
    raise ValueError("Eval Method must be valid")



if __name__=="__main__":
  import sys
  learner, data_file, eval_method, N, train_percent, num_folds= parse_line_params(sys.argv[1:])
  runner(learner, data_file, eval_method, N, train_percent, num_folds)

