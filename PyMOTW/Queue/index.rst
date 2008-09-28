=====
Queue
=====
.. module:: Queue
    :synopsis: Provides a thread-safe FIFO implementation

:Module: Queue
:Purpose: Provides a thread-safe FIFO implementation
:Python Version: at least 1.4

Description
===========

The Queue module provides a FIFO implementation suitable for multi-threaded
programming. It can be used to pass messages or other data between producer
and consumer threads safely. Locking is handled for the caller, so it is
simple to have as many threads as you want working with the same Queue
instance. A Queue's size (number of elements) may be restricted to throttle
memory usage or processing.

This discussion assumes you already understand the general nature of a queue.
If you don't, you may want to read these references before continuing:

* Queue data structures (http://en.wikipedia.org/wiki/Queue_%28data_structure%29)
* FIFO (http://en.wikipedia.org/wiki/FIFO)


Example
=======

As an example of how to use the Queue class with multiple threads, we can
create a very simplistic podcasting client. This client reads one or more RSS
feeds, queues up the enclosures for download, and processes several downloads
in parallel using threads. It is extremely simplistic and is entirely
unsuitable for actual use, but the skeleton implementation gives us enough
code to work with to provide an example of using the Queue module.

To start, we import a few useful modules:

::

    from Queue import Queue

    from threading import Thread
    import time

    import feedparser

Now, let's establish some operating parameters. Normally these would come from
user inputs (preferences, a database, whatever). For our example we hard code
a few values:

::

    # Set up some global variables
    num_fetch_threads = 2
    enclosure_queue = Queue()

    # A real app wouldn't use hard-coded data...
    feed_urls = [ 'http://www.castsampler.com/cast/feed/rss/guest',
                ]

Next, we need to define the function that will run in the worker thread,
processing the downloads. Again, for illustration purposes this only simulates
the download. To actually download the enclosure, check out the urllib module,
which we will cover in a later episode. In our example, we sleep a variable
amount of time, depending on the thread id.

::

    def downloadEnclosures(i, q):
       """This is the worker thread function.
        It processes items in the queue one after

        another.  These daemon threads go into an
        infinite loop, and only exit when
        the main thread ends.
        """
       while True:

           print '%s: Looking for the next enclosure' % i
           url = q.get()

           print '%s: Downloading:' % i, url
           time.sleep(i + 2) # instead of really downloading the URL, we just pretend

           q.task_done()


Once this target function is defined, we can start the worker threads. Notice
that downloadEnclosures() will block on the statement "url = q.get()" until
the queue has something to return, so it is safe to start the threads before
there is anything in the queue.

::

    # Set up some threads to fetch the enclosures
    for i in range(num_fetch_threads):

    worker = Thread(target=downloadEnclosures, args=(i, enclosure_queue,))

    worker.setDaemon(True)
    worker.start()


And now we retrieve the feed contents (using Mark Pilgrim's feedparser module)
and enqueue the URLs of the enclosures. As soon as the first URL is added to
the queue, one of the worker threads should pick it up and start downloading
it. The loop below will continue to add items until the feed is exhausted, and
the worker threads will take turns dequeuing URLs to download them.

::

    # Download the feed(s) and put the enclosure URLs into
    # the queue.
    for url in feed_urls:
       response = feedparser.parse(url, agent='fetch_podcasts.py')

       for entry in response['entries']:
           for enclosure in entry.get('enclosures', []):

               print 'Queuing:', enclosure['url']
               enclosure_queue.put(enclosure['url'])


And the only thing left to do is wait for the queue to empty out again.

::

    # Now wait for the queue to be empty, indicating that we have
    # processed all of the downloads.
    print '*** Main thread waiting'
    enclosure_queue.join()
    print '*** Done'


If you download the sample script and run it without modification, you should
see output something like this:

::

    0: Looking for the next enclosure
    1: Looking for the next enclosure
    Queuing: http://http.earthcache.net/htc-01.media.globix.net/COMP009996MOD1/Danny_Meyer.mp3
    Queuing: http://feeds.feedburner.com/~r/drmoldawer/~5/104445110/moldawerinthemorning_show34_032607.mp3
    Queuing: http://www.podtrac.com/pts/redirect.mp3/twit.cachefly.net/MBW-036.mp3
    Queuing: http://media1.podtech.net/media/2007/04/PID_010848/Podtech_calacaniscast22_ipod.mp4
    Queuing: http://media1.podtech.net/media/2007/03/PID_010592/Podtech_SXSW_KentBrewster_ipod.mp4
    Queuing: http://media1.podtech.net/media/2007/02/PID_010171/Podtech_IDM_ChrisOBrien2.mp3
    Queuing: http://feeds.feedburner.com/~r/drmoldawer/~5/96188661/moldawerinthemorning_show30_022607.mp3
    *** Main thread waiting
    0: Downloading: http://http.earthcache.net/htc-01.media.globix.net/COMP009996MOD1/Danny_Meyer.mp3
    1: Downloading: http://feeds.feedburner.com/~r/drmoldawer/~5/104445110/moldawerinthemorning_show34_032607.mp3
    0: Looking for the next enclosure
    0: Downloading: http://www.podtrac.com/pts/redirect.mp3/twit.cachefly.net/MBW-036.mp3
    1: Looking for the next enclosure
    1: Downloading: http://media1.podtech.net/media/2007/04/PID_010848/Podtech_calacaniscast22_ipod.mp4
    0: Looking for the next enclosure
    0: Downloading: http://media1.podtech.net/media/2007/03/PID_010592/Podtech_SXSW_KentBrewster_ipod.mp4
    0: Looking for the next enclosure
    0: Downloading: http://media1.podtech.net/media/2007/02/PID_010171/Podtech_IDM_ChrisOBrien2.mp3
    1: Looking for the next enclosure
    1: Downloading: http://feeds.feedburner.com/~r/drmoldawer/~5/96188661/moldawerinthemorning_show30_022607.mp3
    0: Looking for the next enclosure
    1: Looking for the next enclosure
    *** Done

YMMV, depending on whether anyone modifies the subscriptions in the guest
account on CastSampler.com.

