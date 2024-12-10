from utils.split_mp3 import split_mp3


if __name__ == '__main__':
    split_mp3('src/heart_song.mp3', '../mp3/heart_song/h', de_silence=0)
    split_mp3('src/heart_mu.mp3', '../mp3/heart_mu/h')
    split_mp3('src/heart_guo.mp3', '../mp3/heart_guo/hg', de_silence=0)
    split_mp3('src/wsz_mu.mp3', '../mp3/wsz/w')
    split_mp3('src/wsz_guo.mp3', '../mp3/wsz/w', start_i=40, st_i=520)
    split_mp3('src/yaoshi.mp3', '../mp3/yaoshi/ys')
    split_mp3('src/karuna_mu.mp3', '../mp3/karuna_mu/k')
    split_mp3('src/karuna_jfq.mp3', '../mp3/karuna_jfq/k')
