### REFERENCES:

- Phonetics for English words are obtained from [CMU Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict) via [g2p-en package](https://anaconda.org/conda-forge/g2p-en).
- IPA to Devanagari mapping was obtained via [ScriptSource](https://www.scriptsource.org/cms/scripts/page.php?item_id=grapheme_detail&uid=a2ys6pbp2u). This mapping has been self-adjusted by Ashish Devkota(me) for completion in [IPA-Devanagari Mapping file](mappings/IPA_Devanagari_mapping_Adapted_to_Arpabet.txt). 
- ARPABET-IPA Mappings are obtained from [SoapBox](https://docs.soapboxlabs.com/resources/linguistics/arpabet-to-ipa/). This is based on original source for arpabet and ipa mappings (via wikipedia): Rice, Lloyd (April 1976). "Hardware & software for speech synthesis". Dr. Dobb's Journal of Computer Calisthenics & Orthodontia. 1 (4): 6–8.
- Additionally the unicode points for Devanagari is obtained from [Devanagari Unicode Chart](https://www.unicode.org/charts/PDF/U0900.pdf).

### PACKAGES

Additional packages required are g2p-en  and pandas. I installed them via conda. But one can use pip as well.
```
conda install [-n <env-name>| -p <env-path>] conda-forge::g2p-en
conda install [-n <env-name>| -p <env-path>] pandas
```

