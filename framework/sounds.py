import pygame

class VirtualChannel:

    def __init__(self, stage):
        self.__curr_channel = None
        self.__prev_channel = None
        self.__cross_fade = 0
        self.__stage = stage
        return

    def play(self, sound, loops, cross_fade=0, offset=0):
        if offset == 0:
            sound_to_play = sound
        else:
            sample = pygame.sndarray.samples(sound)
            sound_to_play = pygame.sndarray.make_sound(sample[int(len(sample) * float(offset)):])
        if cross_fade <= 0:
            if self.__cross_fade != 0:
                if self.__prev_channel != None:
                    self.__prev_channel.stop()
                    self.__prev_channel = None
                self.__stage.stop_timer(self)
                self.__cross_fade = 0
            if self.__curr_channel != None:
                self.__curr_channel.stop()
            sound_len = sound_to_play.get_length()
            if sound_len == 0:
                self.__curr_channel = None
            else:
                self.__curr_channel = sound_to_play.play(loops)
        elif self.__prev_channel != None:
            self.__prev_channel.stop()
        self.__prev_channel = self.__curr_channel
        self.__cross_fade = _div(50 , float(cross_fade))
        sound_len = sound_to_play.get_length()
        if sound_len == 0:
            self.__curr_channel = None
        else:
            self.__curr_channel = sound_to_play.play(loops)
            if self.__curr_channel != None:
                self.__curr_channel.set_volume(0)
        if not self.__stage.is_timer_started(self):
            self.__stage.start_timer(self, min(cross_fade, 50), self.__cross_fade_tick)
        return

    def __cross_fade_tick(self, key, data):
        if self.__prev_channel == None:
            old_volume = 0
        else:
            old_volume = self.__prev_channel.get_volume() - self.__cross_fade
            if old_volume <= 0:
                old_volume = 0
                self.__prev_channel.stop()
                self.__prev_channel = None
            else:
                self.__prev_channel.set_volume(old_volume)
        if self.__curr_channel == None:
            new_volume = 1
        else:
            new_volume = self.__curr_channel.get_volume() + self.__cross_fade
            if new_volume > 1:
                new_volume = 1
            self.__curr_channel.set_volume(new_volume)
        if old_volume == 0 and new_volume == 1:
            self.__stage.stop_timer(key)
            self.__cross_fade = 0
        return


