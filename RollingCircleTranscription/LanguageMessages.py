#FusionAPI_python Addin
#Author-kantoku
#Description-RollingCircleTranscription

import adsk.core, adsk.fusion, traceback

_app = adsk.core.Application.cast(adsk.core.Application.get())
_lang = _app.preferences.generalPreferences.userLanguage


_sDict = {
    # cmd
    'Rolling Circle Transcription':'円転写',
    'It transfers the shape by two circular motions.':'2つの円運動で形状を転送します。',

    # RCT_View
    'A:Base Profile':'A:ベースプロファイル',
    'Select Base Profile':'ベースプロファイルの選択',
    'B:Base Circle':'B:ベースサークル',
    'Select Base Circle':'ベースサークルの選択',
    'C:Target Circle':'C:ターゲットサークル',
    'Select Target Circle':'ターゲットサークルの選択',
    'Tolerance':'トレランス',
    'information':'情報',

    # RCT_Core
    'Base Profile':'ベースプロファイル',
    'Base Circle':'ベースサークル',
    'Target Circle':'ターゲットサークル',
    "It's not an element on the sketch plane :":'それはスケッチ平面上の要素ではありません :',
    "Not on the same plane :":'同一平面上にありません :',
    "The ratio of circles to each other should be a rational number :":'円同士の比率は有理数でなければなりません :',
    'Base Rotation Count':'ベース回転数',
    'Target Rotation Count':'ターゲット回転数',

}


class LanguageMessages:
    @staticmethod
    def sLng(s :str) -> str:

        langs = adsk.core.UserLanguages
        if _lang == langs.EnglishLanguage:
            return s

        if not s in _sDict:
            return s

        return _sDict[s]