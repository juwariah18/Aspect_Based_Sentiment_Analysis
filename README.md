# AspectSentinel

The original HTML, CSS, and JavaScript frontend remains unchanged and runs in a
browser as before. `app.py` is a separate Python review analyzer for a terminal
or Google Colab.

## Run the Python example locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Enter a review when prompted, or press Enter to analyze the sample. The first
run downloads a pretrained product-review model from Hugging Face; an internet
connection is needed for setup. The model runs locally after it is downloaded.

## Run in Google Colab

Run `!pip install torch transformers`, then run `%run /content/app.py`. The
notebook prompts for a review and prints its sentence-level sentiment results.

The Python example uses a pretrained BERT model fine-tuned on product reviews.
Its one-to-five-star probabilities are grouped into negative (one or two
stars), neutral (three stars), and positive (four or five stars). A weak
prediction (below 55%) is shown as neutral rather than forcing a positive or
negative label. The displayed percentage is the model's strongest sentiment
probability. No review examples are manually trained each time the app runs.
