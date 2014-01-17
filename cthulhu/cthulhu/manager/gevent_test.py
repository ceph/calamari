import gevent
from gevent import Timeout

def run_check(name, delay):
  t = Timeout(delay)
  t.start()
  try:
    print name + ' is catching ' + str(delay) + ' ZZZZs'
    gevent.sleep(delay * 2)
  except Timeout, e:
    if e is not t:
      raise
  return name

def watcher(check, name, delay):
  while(1):
    run = gevent.spawn(check, name, delay)
    run.join()
    print run.value + 'has rejoined us'
    print 'processing ' + name

def launch():
  threads = []
  for x,n in (('greg', 5), ('john', 1), ('dan', 4)):
    print "spawning " + x
    watch = gevent.spawn(watcher, run_check, x, n)
    threads.append(watch)

  gevent.joinall(threads)

if __name__ == "__main__":
  print "Launching"
  launch()
