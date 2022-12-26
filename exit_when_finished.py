import modules.scripts as scripts
import gradio as gr
import os
import re
import random

import modules.shared as shared
import modules.sd_samplers

from modules import images
from modules.processing import process_images, Processed, StableDiffusionProcessingTxt2Img
from modules.shared import opts, cmd_opts, state


class Script(scripts.Script):  

    # The title of the script. This is what will be displayed in the dropdown menu.
    def title(self):
        return "Exit When Finished! With Random-Prompt"

    # Determines when the script should be shown in the dropdown menu via the 
    # returned value. As an example:
    # is_img2img is True if the current tab is img2img, and False if it is txt2img.
    # Thus, return is_img2img to only show the script on the img2img tab.
    def show(self, is_img2img):
        return not is_img2img

    # How the script's is displayed in the UI. See https://gradio.app/docs/#components
    # for the different UI components you can use and how to create them.
    # Most UI components can return a value, such as a boolean for a checkbox.
    # The returned values are passed to the run method as parameters.
    def ui(self, is_img2img):
        enable = gr.Checkbox(value=False, label="[Exit-When-Finished] Enable exit function when process is finished.")
        random_prompt_enable = gr.Checkbox(value=False, label="[Random-Prompt] Enable random prompt script function.")
        use_same_seed = gr.Checkbox(value=False, label="[Random-Prompt] Use same seed to generate.")
        return [enable, random_prompt_enable, use_same_seed]        

    def run(self, p, enable, random_prompt_enable, use_same_seed):
        if enable:
            print("[Exit when done]Script is enable. \n")

        proc = None
        if random_prompt_enable:
            print("[Random-Prompt]Script is enable. \n")
            original_prompt = p.prompt[0] if type(p.prompt) == list else p.prompt

            all_prompts = [original_prompt]


            split_str=['']
            right_str=[]
            gen_prompt=''
            new_prompt=''

            for this_prompt in all_prompts:
                for data in re.finditer(r'(<([^>]+)>)', this_prompt):
                    if data:
                        span = data.span(1)
                        new_prompt = this_prompt[:span[0]]
                        gen_prompt = this_prompt[span[0]:]
                        this_str=gen_prompt.replace("<",">")
                        split_str =this_str.split(">")
                        break

            #print(f"new_prompt：{new_prompt}")
            #print(f"gen_prompt：{gen_prompt}")


            split_str[0]=split_str[0].strip()
            split_str[0]=split_str[0].strip(',')
            split_str[0]=split_str[0]+' '
            for in_str in split_str:
                if "|" not in in_str:
                    if "," in in_str:
                        FL_str=in_str.split(",")
                        right_str.append(FL_str[0])
                        right_str.append(FL_str[1])
                    else:
                        right_str.append(in_str)
            #print (right_str)
            #print (len(right_str))
            #d=int((len(right_str)-1)/2)
            #print(d)

            for ip in range(p.n_iter+1):

                my_prompt=""

                i=0
                for data in re.finditer(r'(<([^>]+)>)', gen_prompt):
                    if data:

                        items = data.group(2).split("|")#=list
                        length=len(items)-1

                        rand_item = items[random.randint(0,length)]

                        rand_str=right_str[i]+rand_item+right_str[i+1]

                        my_prompt=my_prompt+rand_str.strip()+","
                        i=i+2

                i_prompt=new_prompt+my_prompt
                all_prompts.append(i_prompt)
                #print(f"i_prompt：{i_prompt}")
                #print(f"all_prompts len：{len(all_prompts)}")

            if gen_prompt != '':
                all_prompts.remove(all_prompts[0])


            p.prompt = all_prompts * p.n_iter #all_prompts * p.n_iter
            if use_same_seed == True:
                p.seed =[item for item in range(int(p.seed), int(p.seed) + p.n_iter) for _ in range(len(all_prompts))]
            #print(f"p.n_iter：{p.n_iter}") #=batch_count
            p.do_not_save_grid = True
            p.prompt_for_display = original_prompt

            proc = process_images(p)
        else:
            proc = process_images(p)

        if enable:
            print("[Exit when done]try exit.\n")
            os._exit(0)

        return proc
