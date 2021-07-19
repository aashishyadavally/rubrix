import json
import os
import tensorflow_hub as hub
import numpy as np
from storyteller import pathfinder

images_path = "../assets/data"
train_captions_path = images_path + "/train_captions.json"
val_captions_path = images_path + "/val_captions.json"



########Load in the embedding model######
###Maybe change this part to load from locally stored model
module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
    #Loading in the large/5 model
model = hub.load(module_url)
    #Now model( list_of_strings ) will embedd the strings in a (numstrings,512) tensor

embeddings_folder = str(pathfinder.get("storyteller","assets","data","embeddings"))
##Ensure the encodings folder exists
if not os.path.exists(embeddings_folder):
    os.mkdir(embeddings_folder)


def embedd_captions(captions_path,this_embeddings_folder):
    """
    embedds all the captions in a json file at captions_path into separate numpy files
    and returns a dictionary of image_id:path_to_embedding

    Arguments:
    ------
        captions_path (string):
            path to the captions.json to embedd
        this_embeddings_folder (string):
            path to the folder to store the numpy embeddings in

    Returns:
    --------
        ids_to_numpy_paths (dict):
            ids_to_numpy_paths[image_id] -> a list of the absolute paths of
            the numpy embeddings of all captions of image_id
    """
    #Initialize the output
    ids_to_numpy_paths = {}
    #Load in the data
    with  open( captions_path, "r") as captions_file:
        ids_captions = json.load(captions_file)["contents"]

    i = 0
    for caption_pair in ids_captions:
        i+=1
        if i % 1000==0:
            print(i)
            
        caption = caption_pair["caption"]
        image_id = caption_pair["image_id"]
        if image_id in ids_to_numpy_paths.keys():
            #if this is not the first time the image has been embedded then we need to
            #add a _(#imagesalreadyembedded+1) to the path of the .npy
            numpy_path = this_embeddings_folder + "/" + image_id[:-4] + "_" \
                    + str(len(ids_to_numpy_paths[image_id]) + 1) + ".npy"
            ids_to_numpy_paths[image_id].append(numpy_path)
        else:
            #If this is the first time this image has been embedded, then _1
            numpy_path = this_embeddings_folder + "/" + image_id[:-4] + "_1.npy"
            ids_to_numpy_paths[image_id] = [numpy_path]
        ##Do the embedding
        embedd_tensor = model( [caption] ) #(1,512) tensor
        embedd_numpy = embedd_tensor.numpy()[0] #(512,) numpy array
        np.save(numpy_path,embedd_numpy)

    return ids_to_numpy_paths


val_ids_to_paths = embedd_captions(val_captions_path,embeddings_folder)
train_and_val = True
if train_and_val:
    train_ids_to_paths = embedd_captions(train_captions_path,embeddings_folder)
    final_dict = {**val_ids_to_paths, **train_ids_to_paths}
else:
    final_dict = val_ids_to_paths

json_embedding_locations = str(pathfinder.get("storyteller","assets","data")) \
                                + "/imageEmbeddingLocations.json"



jsonfile = open(json_embedding_locations,'w')
json.dump(final_dict,jsonfile, indent = 4)
jsonfile.close()
