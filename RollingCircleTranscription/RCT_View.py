#FusionAPI_python Addin
#Author-kantoku
#Description-RollingCircleTranscription

import adsk.core, adsk.fusion, traceback
from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase
from .RCT_Core import RCT_Factry


# inputs
_imgInfo = ['img','','./resources/dialog/Explanation.png']

_selProInfo = ['selPro','A:Base Profile','Select Base Profile',
    ['Profiles']]
_selProIpt :adsk.core.SelectionCommandInput.cast(None)

_selBaseInfo = ['selBase','B:Base Circle','Select Base Circle',
    ['SketchCircles']]
_selBaseIpt :adsk.core.SelectionCommandInput.cast(None)

_selTargetInfo = ['selTarget','C:Target Circle','Select Target Circle',
    ['SketchCircles']]
_selTargetIpt :adsk.core.SelectionCommandInput.cast(None)

dwnStyle = adsk.core.DropDownStyles.TextListDropDownStyle
_dwnToleranceInfo = ['dwnTolerance','Tolerance',dwnStyle,
    {'Low':10, 'Mid':4, 'Hi':2}]
_dwnToleranceIpt :adsk.core.DropDownCommandInput.cast(None)

_stateInfo = ['stateInfo','information','']
_stateInfoIpt :adsk.core.StringValueCommandInput.cast(None)

# other
_fact = None


class RCT_View(Fusion360CommandBase):
    _handlers = []

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        try:
            if changed_input.objectType != 'adsk::core::SelectionCommandInput':
                return

            global _fact
            global _selProIpt, _selBaseIpt, _selTargetIpt

            # ここ清楚に書き直したい
            if changed_input == _selProIpt:
                try:
                    _fact.baseProfile = changed_input.selection(0).entity
                except:
                    _fact.baseProfile = None
            elif changed_input == _selBaseIpt:
                try:
                    _fact.baseCircle = changed_input.selection(0).entity
                except:
                    _fact.baseCircle = None

            elif changed_input == _selTargetIpt:
                try:
                    _fact.targetCircle = changed_input.selection(0).entity
                except:
                    _fact.targetCircle= None


            if changed_input.selectionCount == 0:
                return

            # 何故リスト順にフォーカスが移らないのか謎
            for ipt in [_selProIpt, _selTargetIpt, _selBaseIpt]:
                if ipt.selectionCount == 0:
                    ipt.hasFocus = True

        except:
            AppObjects().ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        try:
            global _dwnToleranceInfo, _dwnToleranceIpt
            key =_dwnToleranceIpt.selectedItem.name
            tolerance :int = _dwnToleranceInfo[3][key]

            global _fact
            surf = _fact.execute(tolerance)
            if not surf:
                return

            # create surface
            _fact.initSurface(surf)

        except:
            AppObjects().ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        command.isPositionDependent = True

        # factry
        global _fact
        _fact = RCT_Factry()

        # event
        onPreSelect = PreSelectHandler()
        command.preSelect.add(onPreSelect)
        self._handlers.append(onPreSelect)

        onValidateInputs = ValidateInputHandler()
        command.validateInputs.add(onValidateInputs)
        self._handlers.append(onValidateInputs)


        # inputs
        global _imgInfo
        inputs.addImageCommandInput(_imgInfo[0], _imgInfo[1], _imgInfo[2])

        global _selProInfo, _selProIpt
        _selProIpt = inputs.addSelectionInput(
            _selProInfo[0], _selProInfo[1], _selProInfo[2])
        _selProIpt.setSelectionLimits(0)
        [_selProIpt.addSelectionFilter(s) for s in _selProInfo[3]]

        global _selBaseInfo, _selBaseIpt
        _selBaseIpt = inputs.addSelectionInput(
            _selBaseInfo[0], _selBaseInfo[1], _selBaseInfo[2])
        _selBaseIpt.setSelectionLimits(0)
        [_selBaseIpt.addSelectionFilter(s) for s in _selBaseInfo[3]]

        global _selTargetInfo, _selTargetIpt
        _selTargetIpt = inputs.addSelectionInput(
            _selTargetInfo[0], _selTargetInfo[1], _selTargetInfo[2])
        _selTargetIpt.setSelectionLimits(0)
        [_selTargetIpt.addSelectionFilter(s) for s in _selTargetInfo[3]]

        global _dwnToleranceInfo, _dwnToleranceIpt
        _dwnToleranceIpt = inputs.addDropDownCommandInput(
            _dwnToleranceInfo[0], _dwnToleranceInfo[1], _dwnToleranceInfo[2])
        dwnItems = _dwnToleranceIpt.listItems
        dic = _dwnToleranceInfo[3]
        [dwnItems.add(key, True, '') for key in dic.keys()]

        global _stateInfo, _stateInfoIpt
        _stateInfoIpt = inputs.addStringValueInput(_stateInfo[0], _stateInfo[1], _stateInfo[2])
        _stateInfoIpt.isReadOnly = True


class PreSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            args = adsk.core.SelectionEventArgs.cast(args)
            args.isSelectable = True

            ipt = args.activeInput
            if ipt.selectionCount == 1:
                args.isSelectable = False

        except:
            AppObjects().ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ValidateInputHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _fact
            res, msg = _fact.canExec()

            if res:
                args.areInputsValid = True
            else:
                args.areInputsValid = False

            global _stateInfoIpt
            _stateInfoIpt.value = msg

        except:
            AppObjects().ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))