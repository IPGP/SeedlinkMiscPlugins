import os
import re

import hashlib

'''
Plugin handler for the miscScript plugin.
'''
class SeedlinkPluginHandler:
  # Create defaults
  def __init__(self): pass

  def push(self, seedlink):

    # Check and set defaults
    try: seedlink.param('sources.miscScript.script_path')
    except: seedlink.setParam('sources.miscScript.script_path', '')

    try: seedlink.param('sources.miscScript.script_args')
    except: seedlink.setParam('sources.miscScript.script_args', 'default')#If no argument, set 'default'

    try: seedlink.param('sources.miscScript.proc')
    except: seedlink.setParam('sources.miscScript.proc', 'auto_miscScript')

    try: seedlink.param('sources.miscScript.sample_frequency')
    except: seedlink.setParam('sources.miscScript.sample_frequency', '1')

    freq=seedlink.param('sources.miscScript.sample_frequency')

    if re.match("[0-9]+$",freq)!=None:
        seedlink.setParam('sources.miscScript.sample_period', str(1.0/int(freq)))
    else :
        res=re.match("([0-9]+)/([0-9]+)$",freq)
        if res != None :
            seedlink.setParam('sources.miscScript.sample_period', str(float(res.group(2))/float(res.group(1))))
        else:
            print("Sample frequency invalid !!!")
            raise Exception

    try: seedlink.param('sources.miscScript.channels')
    except: seedlink.setParam('sources.miscScript.channels', 'HHZ,HHN,HHE')

    splitted_chans=seedlink.param('sources.miscScript.channels').split(',')
    seedlink.setParam('sources.miscScript.channelsNumber',len(splitted_chans))

    try: seedlink.param('sources.miscScript.flush_period')
    except: seedlink.setParam('sources.miscScript.flush_period', '0')

    ##### Auto-generate proc conf and channel/source_id mapping

    if seedlink.param('sources.miscScript.proc') == "auto_miscScript":
        trees=""
        channels=""
        idx=0

        #Hash source id because channel names are 1..10 letters only identifiers.
        hash_id="{:07d}".format(int(hashlib.sha256(seedlink.param('seedlink.source.id').encode('utf-8')).hexdigest(),16)%(10**7))

        for chan in splitted_chans:
            chan=chan.strip()

            if chan=="none":
                idx+=1
                continue

            elif len(chan)==3:
                location_val="00"
                stream_val=chan[0:2]
                channel_val=chan[2]

            elif len(chan)==5:
                location_val=chan[0:2]
                stream_val=chan[2:4]
                channel_val=chan[4]

            else:
                print("Invalid channel name")
                raise Exception;

            trees+="<tree>\n"
            trees+="""<input name="{}" channel="{}" location="{}" rate="{}"/>\n""".format(hash_id+str(idx),channel_val,location_val,seedlink.param('sources.miscScript.sample_frequency'))
            trees+="""<node stream="{}"/>\n""".format(stream_val)
            trees+="</tree>\n"

            channels+="channel {} source_id={}\n".format(hash_id+str(idx),idx)

            idx+=1;

        #endfor

        seedlink.setParam('sources.miscScript.trees',trees)
        seedlink.setParam('sources.miscScript.channels',channels)

    #####

    return seedlink.param('seedlink.source.id')


  # Flush does nothing
  def flush(self, seedlink):
    pass
