#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Electrisense Test
# Generated: Fri Feb 15 15:30:49 2019
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from gnuradio.fft import logpwrfft
from gnuradio.filter import firdes
from optparse import OptionParser

import time
import sys



class data_logger(gr.top_block):
	def __init__(self):
		gr.top_block.__init__(self)

		############# Define variables #############
		self.samp_rate = 1e6
		self.fc = 45e3
		
		self.filename = "/home/zerina/data_logger.bin"
		self.fileNum = 1

		############# Initalize blocks #############
		self.uhd_usrp_source = uhd.usrp_source(
			",".join(('addr=192.168.10.2',"")),
			uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
				),
			)

		self.uhd_usrp_source.set_samp_rate(self.samp_rate)
		self.uhd_usrp_source.set_center_freq(self.fc, 0)
		self.uhd_usrp_source.set_gain(0,0)
		self.uhd_usrp_source.set_antenna('TX/RX', 0)
		self.uhd_usrp_source.set_bandwidth(1e6, 0)

		self.lpwrfft = logpwrfft.logpwrfft_c(
			sample_rate=self.samp_rate,
			fft_size=2048,
			ref_scale=2,
			frame_rate=30,
			avg_alpha=1.0,
			average=False,
		)

		self.file_sink = blocks.file_sink(gr.sizeof_float*2048, self.filename, False)
		self.file_sink.set_unbuffered(False)

		############# Connect blocks #############
		self.connect((self.lpwrfft,0),(self.file_sink,0))
		self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))

	def start_new_file(self):
		print("Starting new file")
		time.sleep(30)
		tb.stop()
		tb.wait()
		#self.disconnect((self.analog_sig_source,0),(self.file_sink,0))
		self.filename = "/home/zerina/data_logging" + str(self.fileNum) + ".bin"
		self.file_sink = blocks.file_sink(gr.sizeof_float*2048, self.filename, False)
		self.connect((self.lpwrfft,0),(self.file_sink,0))
		self.fileNum +=1
		tb.start()
		time.sleep(30)
def main():
	global tb
	tb = data_logger()
	tb.start()

	while 1:
		#c = raw_input("'q' to quite\n")
		tb.start_new_file()
		


if __name__ == '__main__':
	main()
