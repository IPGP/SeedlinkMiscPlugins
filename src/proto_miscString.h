/***************************************************************************** 
 * proto_miscString.h
 *
 * miscString library. Inspired from MODBUS protocol implementation (Andres Heinloo, GFZ Potsdam)
 * Tristan DIDIER, IPGP/OVSG, 2020
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2, or (at your option) any later
 * version. For more information, see http://www.gnu.org/
 *****************************************************************************/


#ifndef DEF_SERIAL_STRING_H
#define DEF_SERIAL_STRING_H

#include <iomanip>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <cstddef>
#include <cmath>
#include <cstring>
#include <cerrno>
#include <unistd.h>
#include <time.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include "qdefines.h"
#include "qtime.h"
#include "utils.h"
#include "cppstreams.h"
#include "serial_plugin.h"
#include "plugin_channel.h"
#include "diag.h"
#include "big-endian.h"

using namespace std;
using namespace Utilities;
using namespace CPPStreams;
using namespace SeedlinkPlugin;

//****************************************************************************
// CONSTANTES
//****************************************************************************

const int MAX_TIME_ERROR    = 1000000; //copied from proto_modbus

//*****************************************************************************
// Data Structures
//*****************************************************************************


//*****************************************************************************
// CLASS miscString_Protocol
//*****************************************************************************


class miscStringProtocol: public Proto
  {
    protected:
    int NCHAN; //configurable with scconfig
    float SAMPLE_PERIOD;//configurable with scconfig
    int FLUSH_PERIOD;//configurable with scconfig
    vector<rc_ptr<OutputChannel> > miscString_channels;//size depending on NCHAN
    int MAXFRAMELENGTH;//depends on NCHAN

    bool startup_message, soh_message;
    int last_day, last_soh;

    time_t nextFlush; //next forced flush date if FLUSH_PERIOD != 0

    //Protected methods
    static void alarm_handler(int sig);
    void handle_response(char* frame);
    void decode_message(char* data);

    //Public methods
    public:
    //Constructeur
    miscStringProtocol(const string &myname);

    //Implementation of virtual methods from Proto class (cf serial_plugin.h)
    void attach_output_channel(const string &source_id,
      const string &channel_name, const string &station_name,
      double scale, double realscale, double realoffset,
      const string &realunit, int precision);
    void flush_channels();
};

#endif
