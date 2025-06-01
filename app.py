from flask import Flask, request, jsonify, render_template, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/image_proxy/<image_id>')
def image_proxy(image_id):
    # Construct the IIIF image URL
    iiif_url = f'https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg'
    try:
        img_res = requests.get(iiif_url, stream=True)
        img_res.raise_for_status()
        return Response(img_res.content, mimetype=img_res.headers.get('Content-Type', 'image/jpeg'))
    except Exception as e:
        # Return a 404 or a placeholder image if fetch fails
        return '', 404

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if request.method == 'POST':
        search = request.json.get('search', '')
        page = int(request.json.get('page', 1))
        limit = 100
        if not search:
            return jsonify({'error': 'No medium provided'}), 400

        url = 'https://api.artic.edu/api/v1/artworks/search'
        params = {
            'q': search,
            'limit': limit,
            'from': (page - 1) * limit,
            'fields': 'id,title,image_id,artist_display,medium,is_public_domain'
        }

        try:
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            artworks = []
            for art in data.get('data', []):
                if art.get('image_id') and art.get('is_public_domain'):
                    artworks.append({
                        'title': art.get('title', 'Untitled'),
                        'artist': art.get('artist_display', 'Unknown'),
                        'medium': art.get('medium', ''),
                        'image_id': art['image_id']
                    })

            return jsonify(artworks)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('explore.html')

@app.route('/artbank')
def artbank():
    return render_template('bank.html')

@app.route('/artscan')
def artscan():
    return render_template('wip.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

