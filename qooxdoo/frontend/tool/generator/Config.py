#!/usr/bin/env python

################################################################################
#
#  qooxdoo - the new era of web development
#
#  http://qooxdoo.org
#
#  Copyright:
#    2006-2008 1&1 Internet AG, Germany, http://www.1und1.de
#
#  License:
#    LGPL: http://www.gnu.org/licenses/lgpl.html
#    EPL: http://www.eclipse.org/org/documents/epl-v10.php
#    See the LICENSE file in the project's top-level directory for details.
#
#  Authors:
#    * Sebastian Werner (wpbasti)
#    * Thomas Herchenroeder (thron7)
#
################################################################################

import os, sys, re, types, string, copy
import simplejson
from generator.ShellCmd import ShellCmd

class Config:
    def __init__(self, console, data, path=""):
        # init members
        self._console  = console
        self._data     = None
        self._fname    = None
        self._shellCmd = ShellCmd()
        
        # dispatch on argument
        if isinstance(data, (types.DictType, types.ListType)):
            self.__init__data(data, path)
        elif isinstance(data, types.StringTypes):
            self.__init_fname(data)
        else:
            raise TypeError, str(data)

    def __init__data(self, data, path):
        self._data = data
        if path:
            self._dirname = os.path.abspath(path)
        else:
            self._dirname = os.getcwd()

    def __init_fname(self, fname):
        obj = open(fname)
        jsonstr = obj.read()
        jsonstr = self._stripComments(jsonstr)
        data = simplejson.loads(jsonstr)
        obj.close()

        self._data  = data
        self._fname = os.path.abspath(fname)
        self._dirname = os.path.dirname(self._fname)

    NSSEP        = "/"
    JOBS_KEY     = "jobs"
    DEFAULTS_KEY = "defaults"
    EXTEND_KEY   = "extend"
    RUN_KEY      = "run"
    #KEYS_WITH_JOB_REFS = ['run', 'extend']
    KEYS_WITH_JOB_REFS = [RUN_KEY, EXTEND_KEY]

    def get(self, key, default=None, confmap=None):
        """Returns a (possibly nested) data element from dict <conf>
        """
        
        if confmap:
            data = confmap
        else:
            data = self._data
            
        if data.has_key(key):
            return data[key]

        splits = key.split(self.NSSEP)
        for part in splits:
            if part == "." or part == "":
                pass
            elif isinstance(data, types.DictType) and data.has_key(part):
                data = data[part]
            else:
                return default

        return data


    def set(self, key, content, AddKeys=False, confmap=None):
        """Sets a (possibly nested) data element in dict <conf>
        """
        if confmap:
            container = confmap
        else:
            container = self._data
        splits = key.split(self.NSSEP)

        # wpbasti: What should this do?
        for item in splits[:-1]:
            if isinstance(container, types.DictType):
                if container.has_key(item):
                    container = container[item]
                else:
                    if AddKeys:
                        container[item] = {}
                        container       = container[item]
                    else:
                        raise KeyError, key
            else:
                raise TypeError, "Missing map for descend"

        container[splits[-1]] = content
        return True
        

    def iter(self):
        result = []
        for item in self._data:
            result.append(Config(self._console, item))
        
        return result
        
        
    def extract(self, key):
        return Config(self._console, self.get(key, {}), self._dirname)
        

    def getJobsMap(self, default=None):
        if self.JOBS_KEY in self._data:
            return self._data[self.JOBS_KEY]
        else:
            return default

    def listJobs(self):
        result = []
        jobsMap = self.getJobsMap({})
        for job in jobsMap:
            result.append(job)
        return result
    
    # wpbasti: specific to top level configs. Should be done in a separate class
    def resolveIncludes(self, includeTrace=[]):

        def integrateExternalConfig_o(target, source, namespace):
            # external config becomes namespace'd entry in jobsmap
            if target.has_key(namespace):
                raise KeyError, "key already exists: " + namespace
            else:
                target[namespace] = source.get(".")
            return target

        def integrateExternalConfig(tjobs, source, namespace):
            # jobs of external config are spliced into current job list
            sjobs = source.getJobsMap()
            if namespace:
                namepfx = namespace + self.NSSEP
            else:
                namepfx = ""
            for sjob in sjobs:
                newjobname = namepfx + sjob
                if tjobs.has_key(newjobname):
                    raise KeyError, "Job already exists: \"%s\"" % newjobname
                else:
                    # patch job references in 'run', 'extend', ... keys
                    for key in self.KEYS_WITH_JOB_REFS:
                        if key in sjobs[sjob]:
                            newlist = []
                            oldlist = sjobs[sjob][key]
                            for jobname in oldlist:
                                newlist.append(namepfx + jobname)
                            sjobs[sjob][key] = newlist
                    # handle 'defaults' job - we have to fix this here at loadtime
                    # so we don't have to worry about nested defaults job when
                    # runExpand runs
                    if sjobs.has_key(self.DEFAULTS_KEY):
                        # the 'defaults' job will be namespaced as well
                        defaults_job_name = namepfx + self.DEFAULTS_KEY
                        if sjobs[sjob].has_key(self.EXTEND_KEY):
                            sjobs[sjob][self.EXTEND_KEY].insert(0, defaults_job_name)
                        else:
                            sjobs[sjob][self.EXTEND_KEY] = [defaults_job_name]
                    # add new job
                    tjobs[newjobname] = sjobs[sjob]
            return tjobs

        config  = self._data
        jobsmap = self.get("jobs")

        if self._fname:   # we stem from a file
            includeTrace.append(self._fname)   # expand the include trace
            
        if config.has_key('include'):
            for namespace, fname in config['include'].iteritems():
                # cycle check
                if os.path.abspath(fname) in includeTrace:
                    self._console.warn("Include config already seen: %s" % str(includeTrace+[os.path.abspath(fname)]))
                    sys.exit(1)
                
                # calculate path relative to config file if necessary
                if not os.path.isabs(fname):
                    fpath = os.path.normpath(os.path.join(self._dirname, fname))
                else:
                    fpath = fname
        
                # wpbasti:
                # If top level configs are a separate class they can do some of this magic automatically
                # e.g. calling resolveIncludes()
                econfig = Config(self._console, fpath)
                econfig.resolveIncludes(includeTrace)   # recursive include
                #jobsmap[namespace] = econfig.get(".")
                jobsmap = integrateExternalConfig(jobsmap, econfig, namespace)


    # wpbasti: specific to top level configs. Should be done in a separate class
    def resolveExtendsAndRuns(self, joblist):
        jobsmap = self.get("jobs")
        console = self._console
        console.info("Resolving jobs...")
        console.indent()

        # while there are still 'run' jobs or unresolved jobs in the job list...
        while ([x for x in joblist if jobsmap[x].has_key('run')] or 
               [y for y in joblist if not jobsmap[y].has_key('resolved')]):
            self._resolveExtends(self._console, jobsmap, joblist)
            self._resolveRuns(self._console, jobsmap, joblist)

        console.outdent()
        return joblist

    def _mapMerge(self, source, target):
        """merge source map into target, but don't overwrite existing
           keys in target (unlike .update())"""
        # wpbasti: Why not just use update() in reversed order (maybe copy target first)???
        t = target.copy()
        for (k,v) in source.items():
            if not t.has_key(k):
                t[k] = v
        return t


    ##                                                                              
    # _resolveRuns -- resolve the 'run' key in a job
    #                                                                               
    # @param     self     (IN) self
    # @param     console  (IN) console object to use for logging
    # @param     jobsmap  (IN/OUT) map of all jobs;
    # @param     jobs     (IN/OUT) list of names of jobs that will be run
    # @return             None
    # @exception RuntimeError  'resolved' key missing in one of jobs' job
    #
    # DESCRIPTION
    #  The 'run' key of a job is a list of jobs to be run in its place, e.g.
    #  'run' : ['jobA', 'jobB']. This indicates how the resolution of the key is
    #  done:
    #  - for each job in the 'run' list, a new job is created ("synthetic jobs")
    #  - the original job serves as a template so the new jobs get all the
    #    settings of the original job (apart from the 'run' key)
    #  - an 'extend' key is set with the particular subjob as its
    #    only member (assuming any original 'extend' key has already been
    #    resolved). - This way all the new jobs can be run as regular jobs,
    #    essentially performing the task of the referenced subjob.
    #  - in the job list, the original job is replaced by the list of new jobs

    # wpbasti: specific to top level configs. Should be done in a separate class
    # Also: Can we do this resolving without a jobs map? Normally, if this is a separate
    # class for handling top-level configs it should be quite easy. To complete resolve
    # all dynamic stuff before finally starting the first jobs still make sense in my opinion
    def _resolveRuns(self, console, jobsmap, jobs):
        i,j = 0, len(jobs)
        while i<j:
            job = jobs[i]
            entry = jobsmap[job]
            if entry.has_key("run"):
                sublist = []
                for subjob in entry["run"]:
                    
                    # make new job map job::subjob as copy of job, but extend[subjob]
                    newjobname = job + '::' + subjob.replace(self.NSSEP,'::')
                    newjob = entry.copy()
                    del newjob['run']       # remove 'run' key
                    
                    # we assume the initial 'run' job has already been resolved, so
                    # we reset it here and set the 'extend' to the subjob
                    if newjob.has_key('resolved'): 
                        del newjob['resolved']
                    else:
                        raise RuntimeError, "Cannot resolve 'run' key before 'extend' key"
                    newjob['extend'] = [subjob] # extend subjob
                    
                    # add to config
                    jobsmap[newjobname] = newjob
                    
                    # add to job list
                    sublist.append(newjobname)
                    
                # replace old job by subjobs list
                jobs[i:i+1] = sublist  
                j = j + len(sublist) - 1
            i += 1


    # wpbasti: specific to top level configs. Should be done in a separate class
    def _resolveExtends(self, console, config, jobs):
        # wpbasti: you know of list1+list2 option?
        def _listPrepend(source, target):
            """returns new list with source prepended to target"""
            l = target[:]
            for i in range(len(source)-1,-1,-1):
                l.insert(0,source[i])
            return l

        def _mergeEntry(target, source):
            for key in source:
                # merge 'library' key rather than shadowing
                if key == 'library'and target.has_key(key):
                    target[key] = _listPrepend(source[key],target[key])
                
                # merge 'settings' and 'let' key rather than shadowing
                # wpbasti: variants listed here, but missing somewhere else. Still missing use and require keys.
                if (key in ['variants','settings','let']) and target.has_key(key):
                    target[key] = self._mapMerge(source[key],target[key])
                if not target.has_key(key):
                    target[key] = source[key]

        def _resolveExtend(console, config, job, entryTrace=[]):
            # resolve the 'extend' entry of a job
            if not self.get(job,False,config):
                raise RuntimeError, "No such job: %s" % job

            data = self.get(job,None,config)

            if data.has_key("resolved"):
                return

            # pre-pend optional 'defauls' job
            if config.has_key(self.DEFAULTS_KEY) and job != self.DEFAULTS_KEY:
                if data.has_key('extend'):
                    data['extend'].insert(0,self.DEFAULTS_KEY)
                else:
                    data['extend'] = [self.DEFAULTS_KEY]

            if data.has_key("extend"):
                # we have to define the context of the current job (ie. its containing map), so
                # we know in which context to evaluate 'extend' entries
                jobcontext = config  # we are top-level

                # loop through 'extend' entries
                extends = data["extend"]
                for entry in extends:
                    # cyclic check: have we seen this already?
                    if entry in entryTrace:
                        console.warn("Extend entry already seen: %s" % str(entryTrace+[job,entry]))
                        sys.exit(1)
                    
                    # make sure this entry job is fully resolved in the correct context
                    _resolveExtend(console, jobcontext, entry, entryTrace + [job])

                    # extract the job definition of the entry from the current jobcontext (mind 3rd param!)
                    pjob = self.get(entry, None, jobcontext )
                    
                    # now merge the fully expanded job into the current job
                    _mergeEntry(data, pjob)

            data["resolved"] = True

        for job in jobs:
            _resolveExtend(console, config, job)


    # wpbasti: In my thinking specific to Jobs? Isn't it? Would a as-late-as-possible resolvement hurt?
    # Or is this already used in run, include, extend sections anywhere? And needed?
    def resolveMacros(self, jobs):
        console = self._console
        config  = self.get("jobs")

        def _expandString(s, mapstr, mapbin):
            assert isinstance(s, types.StringTypes)
            if s.find(r'${') == -1:  # optimization: no macro -> return
                return s
            macro = ""
            sub   = ""
            possiblyBin = re.match(r'^\${(.*)}$', s)   # look for '${...}' as a bin replacement
            if possiblyBin:
                macro = possiblyBin.group(1)
            if macro and (macro in mapbin.keys()):
                sub = mapbin[macro]
            else:
                templ = string.Template(s)
                sub = templ.safe_substitute(mapstr)
            return sub

        def _expandMacrosInValues(configElem, maps):
            """ apply macro expansion on arbitrary values; takes care of recursive data like
                lists and dicts; only actually applies macros when a string is encountered on 
                the way (look for calls to _expandString())"""
            result = configElem  # intialize result
            
            # arrays
            if isinstance(configElem, types.ListType):
                for e in range(len(configElem)):
                    enew = _expandMacrosInValues(configElem[e], maps)
                    if enew != configElem[e]:
                        console.debug("expanding: %s ==> %s" % (str(configElem[e]), str(enew)))
                        configElem[e] = enew
                        
            # dicts
            elif isinstance(configElem, types.DictType):
                for e in configElem:
                    # expand in values
                    enew = _expandMacrosInValues(configElem[e], maps)
                    if enew != configElem[e]:
                        console.debug("expanding: %s ==> %s" % (str(configElem[e]), str(enew)))
                        configElem[e] = enew

                    # expand in keys
                    if ((isinstance(e, types.StringTypes) and
                            e.find(r'${')>-1)):
                        enew = _expandString(e, maps['str'], {}) # no bin expand here!
                        configElem[enew] = configElem[e]
                        del configElem[e]
                        console.debug("expanding key: %s ==> %s" % (e, enew))

            # strings
            elif isinstance(configElem, types.StringTypes):
                result = _expandString(configElem, maps['str'], maps['bin'])

            # leave everything else alone
            else:
                result = configElem

            return result


        def _expandMacrosInLet(letDict):
            """ do macro expansion within the "let" dict """

            keys = letDict.keys()
            for k in keys:
                kval = letDict[k]
                
                # construct a temp. dict of translation maps, for later calls to _expand* funcs
                # wpbasti: Crazy stuff: Could be find some better variable names here. Seems to be optimized for size already ;)
                if isinstance(kval, types.StringTypes):
                    kdicts = {'str': {k:kval}, 'bin': {}}
                else:
                    kdicts = {'str': {}, 'bin': {k:kval}}
                    
                # cycle through other keys of this dict
                for k1 in keys:
                    if k != k1: # no expansion with itself!
                        enew = _expandMacrosInValues(letDict[k1], kdicts)
                        if enew != letDict[k1]:
                            console.debug("expanding: %s ==> %s" % (k1, str(enew)))
                            letDict[k1] = enew
            return letDict


        console.info("Resolving macros...")
        console.indent()

        # wpbasti: Iteration through all jobs would also solve this extra-if which is not needed then anymore
        for job in jobs:
            if not config.has_key(job):
                console.warn("No such job: %s" % job)
                sys.exit(1)
            else:
                if config[job].has_key('let'):
                    
                    # exand macros in the let
                    config[job]['let'] = _expandMacrosInLet(config[job]['let'])
                    cfglet = config[job]['let']
                    
                    # separate strings from other values
                    letmaps = {}
                    letmaps['str'] = {}
                    letmaps['bin'] = {}
                    for k in cfglet:
                        if isinstance(cfglet[k], types.StringTypes):
                            letmaps['str'][k] = cfglet[k]
                        else:
                            letmaps['bin'][k] = cfglet[k]
                            
                    # apply dict to other values
                    _expandMacrosInValues(config[job], letmaps)

        console.outdent()


    # wpbasti: specific to file loading => Should be a separate class
    def _stripComments(self,jsonstr):
        eolComment = re.compile(r'//.*$', re.M)
        mulComment = re.compile(r'/\*.*?\*/', re.S)
        result = eolComment.sub('',jsonstr)
        result = mulComment.sub('',result)
        return result


    # wpbasti: specific to top level config => Should be a separate class
    def resolveLibs(self, jobs):
        config  = self.get("jobs")
        console = self._console

        console.info("Resolving libs/manifests...")
        console.indent()

        for job in jobs:
            if not config.has_key(job):
                console.warn("No such job: %s" % job)
                sys.exit(1)
            else:
                if config[job].has_key('library'):
                    newlib = config[job]['library']
                    for lib in newlib:
                        # handle downloads
                        manifest = lib['manifest']
                        manipath = os.path.dirname(manifest)
                        manifile = os.path.basename(manifest)
                        
                        # wpbasti: Seems a bit crazy to handle this here
                        # What's about to process all "remote" manifest initially on file loading?
                        if manipath.startswith("contrib://"): # it's a contrib:// lib
                            contrib = manipath.replace("contrib://","")
                            if config[job].has_key('cache-downloads'):
                                contribCachePath = config[job]['cache-downloads']['path']
                            else:
                                contribCachePath = "cache-downloads"
                            self._download_contrib(newlib, contrib, contribCachePath)
                            manifest = os.path.join(contribCachePath, contrib, manifile)
                            lib['manifest'] = manifest  # patch 'manifest' entry to download path
                        else:  # patch the path which is local to the current config
                            pass # TODO: use manipath and config._dirname, or fix it when including the config
                            
                        # get the local Manifest
                        manifest = Manifest(manifest)
                        lib = manifest.patchLibEntry(lib)

        console.outdent()


    def _download_contrib(self, libs, contrib, contribCache):
        # try to find $FRAMEWORK/tool/modules/download-contrib.py
        # wpbasti: Really want to use the old module here???
        # Should this really require us to do shell commands. Not a good think in my opinion
        # Need a cleaner way here. Maybe a custom class under "generator"
        dl_script    = "download-contrib.py"
        self._console.info("Downloading contribs...")
        self._console.indent()
        for lib in libs:
            path = os.path.dirname(lib['manifest'])
            pathToScript = os.path.join(path, "tool", "modules", dl_script)
            self._console.info("trying download script: " + pathToScript)
            if os.path.exists(pathToScript):
                break
        else:
            self._console.warn("Unable to locate download script for contribs: " + dl_script)
            sys.exit(1)
            
        cmd = "python %s --contrib %s --contrib-cache %s" % tuple(
                    x.replace(" ","\ ") for x in (pathToScript, contrib, contribCache))
        rc = self._shellCmd.execute(cmd)
        self._console.outdent()
        return rc



# wpbasti: TODO: Put into separate file
class Job(object):
    def __init__(self, data, config=None):
        self._data   = data
        self._config = config

    def getData(self):
        return self._data

    def _listPrepend(source, target):
        pass
    
    def _mergeEntry(target, source):
        pass

    def resolveExtend(self, console, config, entryTrace=[]):
        pass

# wpbasti: TODO: Put into separate file
class Manifest(object):
    def __init__(self, path):
        mf = open(path)
        manifest = simplejson.loads(mf.read())
        mf.close()
        self._manifest = manifest

    def patchLibEntry(self, libentry):
        '''Patches a "library" entry with the information from Manifest'''
        libinfo   = self._manifest['provides']
        #uriprefix = libentry['uri']
        uriprefix = ""
        libentry['class']         = os.path.join(uriprefix,libinfo['class'])
        libentry['resource']      = os.path.join(uriprefix,libinfo['resource'])
        libentry['translation']   = os.path.join(uriprefix,libinfo['translation'])
        libentry['encoding']    = libinfo['encoding']
        if 'namespace' not in libentry:
            libentry['namespace']   = libinfo['namespace']
        libentry['type']        = libinfo['type']
        libentry['path']        = os.path.dirname(libentry['manifest']) or '.'

        return libentry


