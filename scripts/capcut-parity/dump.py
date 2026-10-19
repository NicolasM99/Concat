import json, sys, importlib
sys.path.insert(0, sys.argv[1])
out = {}
mods = {
 "transition": ("pyJianYingDraft.metadata.capcut_transition_meta", ["CapCut_Transition_type"]),
 "effect": ("pyJianYingDraft.metadata.capcut_effect_meta", ["CapCut_Video_scene_effect_type","CapCut_Video_character_effect_type"]),
 "animation": ("pyJianYingDraft.metadata.capcut_animation_meta", ["CapCut_Intro_type","CapCut_Outro_type","CapCut_Group_animation_type"]),
 "text_animation": ("pyJianYingDraft.metadata.capcut_text_animation_meta", ["CapCut_Text_intro","CapCut_Text_outro","CapCut_Text_loop_anim"]),
 "mask": ("pyJianYingDraft.metadata.capcut_mask_meta", ["CapCut_Mask_type"]),
 "audio": ("pyJianYingDraft.metadata.capcut_audio_effect_meta", ["CapCut_Voice_filters_effect_type","CapCut_Voice_characters_effect_type","CapCut_Speech_to_song_effect_type"]),
 "filter": ("pyJianYingDraft.metadata.filter_meta", None),
}
for key,(mod,classes) in mods.items():
    m = importlib.import_module(mod)
    if classes is None:
        classes = [n for n in dir(m) if n.endswith("_type") or n.endswith("Type")]
    for c in classes:
        cls = getattr(m, c)
        for member in cls:
            v = member.value
            d = {"class": c, "enum": member.name, "name": getattr(v, "name", member.name)}
            for a in ("is_vip","is_overlap","default_duration","duration"):
                if hasattr(v,a): d[a]=getattr(v,a)
            if hasattr(v,"params"):
                d["params"]=[{"name":p.name,"default":p.default_value,"min":p.min_value,"max":p.max_value} for p in v.params]
            out.setdefault(key,[]).append(d)
json.dump(out, open(sys.argv[2],"w",encoding="utf-8"), indent=1, ensure_ascii=False)
for k,v in out.items(): print(k, len(v), len({x["name"] for x in v}))
