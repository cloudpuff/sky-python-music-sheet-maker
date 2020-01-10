#!/usr/bin/env python3
from modes import InputMode, RenderMode, CSSMode, ResponseMode
from parsers import SongParser
from songs import Song
import os
import re


class Responder:

    def __init__(self):

        self.song_dir_in = "test_songs"
        self.song_dir_out = "songs_out"
        self.css_path = "css/main.css"
        self.css_mode = CSSMode.EMBED
        self.render_modes_enabled = [mode for mode in RenderMode]
        # self.render_modes_disabled = [RenderMode.JIANPUASCII, RenderMode.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]
        # self.render_modes_enabled = [RenderMode.PNG, RenderMode.SKYASCII, RenderMode.WESTERNASCII]

        self.response_mode = ''

        self.song = None
        self.parser = None

        self.cwd = os.getcwd()
        self.init_working_directory()

    def init_working_directory(self):

        os.chdir("../..")
        if not os.path.isdir(self.song_dir_out):
            os.mkdir(self.song_dir_out)

    def get_song_dir_out(self):

        return self.song_dir_out

    def get_css_mode(self):

        return self.css_mode

    def get_css_path(self):

        return self.css_path

    def get_render_modes_enabled(self):

        return self.render_modes_enabled

    def is_render_mode_enabled(self, mode):

        if mode in self.render_modes_enabled:
            return True
        else:
            return False

    def get_song(self):

        return self.song

    def set_song(self, song):

        self.song = song

    def get_parser(self):

        return self.parser

    def ask_for_mode(self, modes):

        modes_list = {}
        instructions = ""
        i = 0
        instructions += "Please choose your note format:\n'"
        for mode in modes:
            i += 1
            instructions += str(i) + ') ' + mode.value[2] + "\n"
            if mode == InputMode.SKYKEYBOARD:
                instructions += "   " + self.get_parser().get_keyboard_layout().replace(" ", "\n   ") + ":"
            modes_list[i] = mode
        self.output(instructions)
        try:
            notation = int(self.ask('Mode (1-' + str(i) + "): ").strip())
            mode = modes_list[notation]
        except (ValueError, KeyError):
            mode = InputMode.SKY
        return mode

    def set_response_mode(self, response_mode):

        # bot or commandline
        self.response_mode = response_mode

    def get_response_mode(self):

        return self.response_mode

    def ask(self, question):

        if self.get_response_mode() == ResponseMode.BOT:

            # TODO: I don't know how to do this
            pass

        elif self.get_response_mode() == ResponseMode.COMMAND_LINE:

            user_response = input(question)

        return user_response

    def output(self, output):

        pass

    def load_file(self, directory, filename):
        """
        if string is a file name, loads the file, else return None
        """
        file_path = os.path.join(directory, os.path.normpath(filename))
        isfile = os.path.isfile(file_path)

        # Assumes that user has forgotten extension
        if not isfile:
            file_path = os.path.join(filename, os.path.normpath(filename + '.txt'))
            isfile = os.path.isfile(file_path)

        if not isfile:
            file_path = None
            splitted = os.path.splitext(filename)
            if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
                # then probably a file name
                while file_path is None:
                    print('\nFile not found.')
                    file_path = self.load_file(directory,
                                               input('File name (in ' + os.path.normpath(directory) + '/): ').strip())
                    isfile = os.path.isfile(file_path)
        if isfile:
            return file_path
        else:
            return None

    def read_lines(self, first_line, filepath=None):
        """
         Read song lines in fp, or asks the user to type each line in the console
        """

        if self.get_response_mode() == ResponseMode.COMMAND_LINE:
            lines = []
            if filepath is not None:
                try:
                    for line in open(filepath, mode='r', encoding='utf-8', errors='ignore'):
                        lines.append(line)
                except (OSError, IOError) as err:
                    print('Error opening file.')
                    raise err
                print('(Song imported from ' + os.path.abspath(filepath) + ')')
            else:
                line = first_line
                while line:
                    line = line.split(os.linesep)
                    for line in line:
                        lines.append(line)
                    line = input('Type next line: ')
            return lines

    def ask_song_title(self):

        self.get_song().set_title(self.ask('Song title (also used for the file name): '))
        if self.get_song().get_title() == '':
            self.get_song().set_title('untitled')

    def ask_song_headers(self):
        print('\nPlease fill song info or press ENTER to skip:')
        original_artists = self.ask('Original artist(s): ')
        transcript_writer = self.ask('Transcribed by: ')
        self.get_song().set_headers(original_artists, transcript_writer, song_key)

    def ask_input_mode(self):

        possible_modes = self.get_parser().get_possible_modes(song_lines)

        if len(possible_modes) > 1:
            print('\nSeveral possible notations detected.')
            input_mode = self.ask_for_mode(possible_modes)
        elif len(possible_modes) == 0:
            print('\nCould not detect your note format. Maybe your song contains typo errors?')
            input_mode = self.ask_for_mode(possible_modes)
        else:
            print('\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.')
            input_mode = possible_modes[0]

        self.get_parser().set_input_mode(input_mode)

    def ask_song_key(self):

        """Attempts to detect key for input written in absolute musical scales (western, Jianpu)"""
        possible_keys = []
        song_key = None
        if song_notation in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
            possible_keys = self.get_parser().find_key(song_lines)
            if len(possible_keys) == 0:
                print("\nYour song cannot be transposed exactly in Sky.")
                # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
                print("\nDefault key will be set to C.")
                song_key = 'C'
            elif len(possible_keys) == 1:
                song_key = str(possible_keys[0])
                print("\nYour song can be transposed in Sky with the following key: " + song_key)
            else:
                print("\nYour song can be transposed in Sky with the following keys: " + ', '.join(possible_keys))
                song_key = ''
                while song_key not in possible_keys:
                    song_key = str(input('Choose your key: '))
        else:
            song_key = str(input('Recommended key to play the visual pattern: '))

        english_song_key = self.get_parser().english_note_name(song_key)

    def ask_note_shift(self):

        if self.get_parser().get_input_mode() in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU,
                                                  InputMode.ENGLISHCHORDS]:
            try:
                note_shift = int(7 * eval(input('Shift song by how many octaves? (-n ; +n): ').strip()))
            except (NameError, SyntaxError):
                note_shift = 0
        else:
            note_shift = 0

    def parse_song(self):

        # Parses song line by line
        song = Song(english_song_key)  # The song key must be in English format
        for song_line in song_lines:
            instrument_line = self.get_parser().parse_line(song_line, song_key,
                                                           note_shift)  # The song key must be in the original format
            song.add_line(instrument_line)

    def calculate_error_ratio(self):
        print('============================================================')
        error_ratio = self.get_song().get_num_broken() / max(1, self.get_song().get_num_instruments())
        if error_ratio == 0:
            print('Song successfully read with no errors!')
        elif error_ratio < 0.05:
            print('Song successfully read with few errors!')
        else:
            print('**WARNING**: Your song contains many errors. Please check the following:'
                  '\n- All your notes are within octaves 4 and 6. If not, try again with an octave shift.'
                  '\n- Your song is free of typos. Please check this website for full instructions: '
                  'https://sky.bloomexperiment.com/t/summary-of-input-modes/403')

    def write_songs(self):

        """Renders the song"""

        if self.is_render_mode_enabled(RenderMode.HTML):
            html_path = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '.html')
            html_path = self.get_song().write_html(html_path, self.get_css_mode(), self.get_css_path())

            if html_path != '':
                print('============================================================')
                print('Your song in HTML is located at:', html_path)

        if self.is_render_mode_enabled(RenderMode.SVG):
            svg_path0 = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '.svg')
            filenum, svg_path = self.get_song().write_svg(svg_path0, self.get_css_mode(), self.get_css_path())

            if svg_path != '':
                print('--------------------------------------------------')
                print('Your song in SVG is located in:', self.get_song_dir_out())
                print('Your song has been split into ' + str(filenum + 1) + ' files '
                                                                            'between ' + os.path.split(svg_path0)[
                          1] + ' and ' + os.path.split(svg_path)[1])

        if self.is_render_mode_enabled(RenderMode.PNG):
            png_path0 = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '.png')
            filenum, png_path = self.get_song().write_png(png_path0)

            if png_path != '':
                print('--------------------------------------------------')
                print('Your song in PNG is located in:', self.get_song_dir_out())
                print('Your song has been split into ' + str(filenum + 1) + ' files '
                                                                            'between ' + os.path.split(png_path0)[
                          1] + ' and ' + os.path.split(png_path)[1])

        if self.is_render_mode_enabled(RenderMode.MIDI):
            midi_path = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '.mid')
            midi_ascii_path = self.get_song().write_midi(midi_path)
            if midi_ascii_path != '':
                print('--------------------------------------------------')
                print('Your song in MIDI is located at:', midi_ascii_path)

        if self.is_render_mode_enabled(RenderMode.SKYASCII) and self.get_parser().get_input_mode() not in [
                InputMode.SKY, InputMode.SKYKEYBOARD]:
            sky_ascii_path = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '_sky.txt')
            res = self.get_song().write_ascii(sky_ascii_path, RenderMode.SKYASCII)
            if sky_ascii_path != '':
                print('--------------------------------------------------')
                print('Your song in TXT converted to Sky notation is located at:', sky_ascii_path)

        if self.is_render_mode_enabled(RenderMode.ENGLISHASCII) and self.get_parser().get_input_mode() not in [
                InputMode.ENGLISH,
                InputMode.ENGLISHCHORDS]:
            english_ascii_path = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '_english.txt')
            english_ascii_path = self.get_song().write_ascii(english_ascii_path, RenderMode.ENGLISHASCII)
            if english_ascii_path != '':
                print('--------------------------------------------------')
                print('Your song in TXT converted to English notation with C key is located at:', english_ascii_path)

        if self.is_render_mode_enabled(
                RenderMode.JIANPUASCII) and self.get_parser().get_input_mode() != InputMode.JIANPU:
            jianpu_ascii_path = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '_jianpu.txt')
            jianpu_ascii_path = self.get_song().write_ascii(jianpu_ascii_path, RenderMode.JIANPUASCII)
            if jianpu_ascii_path != '':
                print('--------------------------------------------------')
                print('Your song in TXT converted to Jianpu notation with 1 key is located at:', jianpu_ascii_path)

        if self.is_render_mode_enabled(
                RenderMode.DOREMIASCII) and self.get_parser().get_input_mode() != InputMode.DOREMI:
            doremi_ascii_path = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + '_doremi.txt')
            doremi_ascii_path = self.get_song().write_ascii(doremi_ascii_path, RenderMode.DOREMIASCII)
            if doremi_ascii_path != '':
                print('--------------------------------------------------')
                print('Your song in TXT converted to doremi notation with do key is located at:', doremi_ascii_path)
