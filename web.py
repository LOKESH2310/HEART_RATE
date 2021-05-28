from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import imageio

app = Flask(__name__, template_folder="client/templates" , static_folder= "client/static")

images = {'happy': 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fdribbble.com%2Fshots%2F6002271-Happy-Heart-like-button&psig=AOvVaw1FDy-kBX-uKKZxN_MoaXUH&ust=1622227080920000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCNDd-fTB6vACFQAAAAAdAAAAABAI',
          'sad': 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.heart.pics%2Ftags%2Fanimations.php&psig=AOvVaw1Y55SdUZZP2wRtA7g21SNK&ust=1622227150340000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCMjin57B6vACFQAAAAAdAAAAABAI',
          'cry': 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fgifer.com%2Fen%2Fgifs%2Fheartbroken&psig=AOvVaw1Y55SdUZZP2wRtA7g21SNK&ust=1622227150340000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCMjin57B6vACFQAAAAAdAAAAABAD'
          }

@app.route('/', methods = ["GET","POST"])
def upload_file():
    if request.method == "GET":
        return render_template("index.html")
    else:
        uploaded_file = request.files['file']
        uploaded_file.save(uploaded_file.filename)
        fps = 30

        # post processing
        vid = imageio.get_reader("sample.mp4", 'ffmpeg')
        colors = {'red': [], 'green': [], 'blue': []}
        for frame in vid:
            pixel = np.mean(frame, axis=(0, 1))
            colors['red'].append(pixel[0])
            colors['green'].append(pixel[1])
            colors['blue'].append(pixel[2])
        for key in colors:
            colors[key] = np.divide(colors[key], 255)
        x = np.arange(len(colors['red'])) / fps

        # filtering
        colors['red_filt'] = list()
        colors['red_filt'] = np.append(colors['red_filt'], colors['red'][0])
        part = 0.25
        sample = fps
        total = part / (part + 2 / sample)
        for index, frame in enumerate(colors['red']):
            if index > 0:
                y_prev = colors['red_filt'][index - 1]
                x_curr = colors['red'][index]
                x_prev = colors['red'][index - 1]
                colors["red_filt"] = np.append(colors['red_filt'], total * (y_prev + x_curr - x_prev))
        x_filt = x[50:-1]
        colors['red_filt'] = colors['red_filt'][50:-1]
        red_fft = np.absolute(np.fft.fft(colors['red_filt']))
        N = len(colors['red_filt'])
        freqs = np.arange(0, sample / 2, sample / N)
        red_fft = red_fft[0:len(freqs)]

        # finding pulse rate
        max_val = 0
        max_index = 0
        for index, fft_val in enumerate(red_fft):
            if fft_val > max_val:
                max_val = fft_val
                max_index = index
        heartrate = freqs[max_index] * 60
        if heartrate < 60:
            img= images['cry']
        elif 60 <= heartrate <=70 :
            img= images['sad']
        elif heartrate > 70:
            img= images['happy']
        return render_template("index.html", heart= heartrate, image= img)

if __name__ == "__main__":
    app.run(debug=True)