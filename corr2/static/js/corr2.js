var corrModel = {};
var $inTotFields;
var $mandatoryFields;

function getDataStr($el, name) {
    var attr = $el.attr('data-' + name);
    if (typeof attr !== 'undefined' && attr !== false) {
        return attr;
    }

    return null;
}

function getDataBool($el, name) {
    var dataStr = getDataStr($el, name);
    if (dataStr === null) {
        return false;
    }

    return dataStr.toLowerCase() == "true";
}

function getDataFloat($el, name) {
    var dataStr = getDataStr($el, name);
    if (dataStr === null) {
        return null;
    } else {
        return parseFloat(dataStr);
    }
}

function isEmptyInput($input) {
    var val = $input.val();
    return val.match(/^\s*$/) ? true : false;
}

function isEmptyField($field) {
    return isEmptyInput(getFieldInput($field));
}

function getLeftFieldsCount() {
    // count only left mandatory fields
    var count = 0;
    $mandatoryFields.each(function() {
        if (isEmptyInput(getFieldInput($(this)))) {
            count++;
        }
    });

    return count;
}

function setFieldInputValue($field, val) {
    getFieldInput($field).val(val);
}

function initInTotFieldsEmpty() {
    $inTotFields.find('input').val('');
}

function initInTotFieldsDef() {
    $inTotFields.each(function() {
        var def = getDataStr($(this), 'default');
        if (def !== null) {
            setFieldInputValue($(this), def);
        } else {
            setFieldInputValue($(this), '');
        }
    });
}

function initInTotFieldsMax() {
    $inTotFields.each(function() {
        var max = getFieldMax($(this));
        getFieldInput($(this)).val(max);
    });
}

function initInTotFieldsZero() {
    $inTotFields.find('input').val('0');
}

function initInTotFields() {
    // save this list for further computation
    $inTotFields = $('.input-row.grade[data-intot="true"]');

    // init fields
    initCbs = {
        'max': initInTotFieldsMax,
        'empty': initInTotFieldsEmpty,
        'zero': initInTotFieldsZero,
        'default': initInTotFieldsDef
    };
    initCbs[corrModel.init]();
}

function initMandatoryFields() {
    $mandatoryFields = $('.input-row.grade[data-intot="true"], .input-row[data-mandatory="true"]');
}

function isInTot($field) {
    return getDataBool($field, 'intot');

}

function getFieldInput($field) {
    return $field.find('.input > *');
}

function validateGradeField($field) {
    if (isInTot($field)) {
        var $input = getFieldInput($field);
        return isValidGrade($input.val());
    }

    return true;
}

function validateField($field) {
    var valid = false;
    if ($field.hasClass('grade')) {
        valid = validateGradeField($field);
    } else if ($field.hasClass('gen')) {
        valid = !isEmptyField($field);
    }

    return valid;
}

function validateForm() {
    var validForm = true;

    // verify each mandatory field
    $mandatoryFields.each(function() {
        var $field = $(this);
        var valid = validateField($field);
        if (!valid) {
            validForm = false;
            $field.addClass('error');
        } else {
            $field.removeClass('error');
        }
    });

    return validForm;
}

function initSaveAction() {
    $('#corr form').submit(function(e) {
        if (validateForm()) {
            if (confirm('save?')) {
                return true;
            }
        }

        return false;
    });
}

function registerInTotFieldsAction($btn, actionCb) {
    $btn.click(function() {
        actionCb();
        updateStatus();
    })
}

function initInTotFieldsActions() {
    // max
    registerInTotFieldsAction($('#btn-max'), initInTotFieldsMax);

    // zero
    registerInTotFieldsAction($('#btn-zero'), initInTotFieldsZero);

    // empty
    registerInTotFieldsAction($('#btn-empty'), initInTotFieldsEmpty);

    // default
    registerInTotFieldsAction($('#btn-def'), initInTotFieldsDef);
}

function isValidGrade(str) {
    return str.match(/^-?\s*\d{1,}(\.\d{1,})?\s*$/) ? true : false;
}

function formatTotal(totalVal) {
    var total = totalVal.toFixed(3);
    if (total.match(/\.0+$/)) {
        total = total.replace(/\.0+$/, '');
    } else {
        total = total.replace(/0+$/, '');
    }

    return total;
}

function updateStatus() {
    // total
    var total = 0;
    $inTotFields.each(function() {
        var $input = getFieldInput($(this));
        var grade = $input.val();
        if (isValidGrade(grade)) {
            total += parseFloat(grade);
        }
    });
    if (total < 0 && !corrModel.allowTotalUnderflow) {
        total = 0;
    } else if (total > corrModel.maxTotal && !corrModel.allowTotalOverflow) {
        total = corrModel.maxTotal;
    }

    $('#total').text(formatTotal(total));

    // left fields count
    var leftFieldsCount = getLeftFieldsCount();
    var str = 'ready to submit';
    var klass = 'good';
    if (leftFieldsCount > 0) {
        var plural = '';
        if (leftFieldsCount > 1) {
            plural = 's';
        }
        str = leftFieldsCount + ' field' + plural + ' left';
        klass = 'bad';
    }
    $('#left-fields').text(str);
    $('#left-fields').removeClass('good');
    $('#left-fields').removeClass('bad');
    $('#left-fields').addClass(klass);
}

function getInputField($input) {
    return $($input).closest('.input-row');
}

function initRowsActions() {
    // focus inner input when clicked
    $('.input-row').click(function() {
        $(this).find('.input > *').focus();
    });


    $('.input-row .input > *').focus(function() {
        $field = getInputField($(this));

        // highlight its row when input has focus
        $field.addClass('selected');

        // show info
        $info = $field.find('.info');
        if ($info.length == 1) {
            $('#info').html($info.html());
            $('#info-box').fadeIn(150);
        } else {
            $('#info-box').fadeOut(150);
        }
    }).blur(function() {
        // remove highlight when losing focus
        getInputField($(this)).removeClass('selected');
    }).keyup(function(e) {
        // every keypress, update status
        updateStatus();

        // remove error class when an input changes
        getInputField($(this)).removeClass('error');
    });

    // buttons
    $('.input-row.grade .buttons .btn').click(function() {
        var $field = $(this).closest('.input-row');
        var $input = getFieldInput($field);
        var val = getDataStr($(this), 'val');
        if (val !== null) {
            $input.val(val);
            updateStatus();
        }
    });
}

function focusField($field) {
    getFieldInput($field).focus();
}

function initFocusFirstField() {
    focusField($('.input-row:first'));
}

function getCurrentField() {
    return $('.input-row.selected');
}

function gotoPreviousField() {
    // current field
    var $curField = getCurrentField();

    // previous field
    var $prevField = null;
    var found = false;
    $('.input-row.gen, .input-row.grade').each(function() {
        if ($(this).get(0) == $curField.get(0)) {
            found = true;
        }
        if (!found) {
            $prevField = $(this);
        }
    });

    if (found && $prevField !== null) {
        focusField($prevField);
        updateStatus();
    }
}

function gotoNextField() {
    // current field
    var $curField = getCurrentField();

    // next field
    var $nextField = null;
    var takeNext = false;
    $('.input-row.gen, .input-row.grade').each(function() {
        if (takeNext) {
            $nextField = $(this);
            takeNext = false;
        }
        if ($(this).get(0) == $curField.get(0)) {
            takeNext = true;
        }
    });

    // focus
    if ($nextField !== null) {
        focusField($nextField);
        updateStatus();
    }
}

function getSectionFirstField($section) {
    return $section.find('.input-row.gen, .input-row.grade').first();
}

function gotoRelativeSection(cb) {
    // current field
    var $curField = getCurrentField();

    // its section
    var $curSection = $curField.parent();

    // relative section
    var $relSection = cb($curSection);

    // goto first field
    if ($relSection.length == 1) {
        // first field
        $firstField = getSectionFirstField($relSection);
        console.log($firstField);
        if ($firstField.length == 1) {
            focusField($firstField);
        }
    }
}

function gotoPreviousSection() {
    gotoRelativeSection(function($section) {
        return $section.prev('.section');
    });
}

function gotoNextSection() {
    gotoRelativeSection(function($section) {
        return $section.next('.section');
    });
}

function getFieldMax($field) {
    var max = getDataFloat($field, 'max');
    if (max < 0) {
        max = 0;
    }

    return max;
}

function applyMaxFracCurrentField(frac) {
    // current field and its input
    var $curField = getCurrentField();
    var $input = getFieldInput($curField);
    $input.val(getFieldMax($curField) * frac);
    updateStatus();
}

function submitForm() {
    $('#corr form').submit();
}

function initKeysActions() {
    $('.input-row input').keydown(function(e) {
        switch (e.keyCode) {
            case 13:
                e.preventDefault();
                if (e.ctrlKey) {
                    // Ctrl+Enter
                    submitForm();
                } else {
                    // Enter
                    gotoNextField();
                }
                break;

            case 40:
                e.preventDefault();
                if (e.ctrlKey) {
                    // Ctrl+Down
                    gotoNextSection();
                } else {
                    // Down
                    gotoNextField();
                }
                break;

            case 38:
                e.preventDefault();
                if (e.ctrlKey) {
                    // Ctrl+Up
                    gotoPreviousSection();
                } else {
                    // Up
                    gotoPreviousField();
                }
                break;
        }
    });
    $('.input-row.grade input').keydown(function(e) {
        switch (e.keyCode) {
            case 90:
                // z
                e.preventDefault();
                applyMaxFracCurrentField(0);
                break;

            case 88:
            case 32:
                // x, space
                e.preventDefault();
                applyMaxFracCurrentField(1);
                break;

            case 65:
                // a
                e.preventDefault();
                applyMaxFracCurrentField(0.25);
                break;

            case 83:
                // s
                e.preventDefault();
                applyMaxFracCurrentField(0.5);
                break;

            case 68:
                // d
                e.preventDefault();
                applyMaxFracCurrentField(0.75);
                break;
        }
    });
}

function initStatus() {
    // set max total
    $('#max-total').text(corrModel.maxTotal);

    // update status now
    updateStatus();
}

function initCorrModel() {
    var $corr = $('#corr');

    // maximum total
    corrModel.maxTotal = parseFloat(getDataStr($corr, 'max-total'));

    // allow overflow
    corrModel.allowTotalOverflow = getDataBool($corr, 'allow-total-overflow');

    // allow underflow
    corrModel.allowTotalUnderflow = getDataBool($corr, 'allow-total-underflow');

    // init action
    corrModel.init = getDataStr($corr, 'init');
}

function init() {
    initCorrModel();
    initInTotFields();
    initMandatoryFields();
    initInTotFieldsActions();
    initRowsActions();
    initKeysActions();
    initSaveAction();
    initStatus();
    initFocusFirstField();
}

$(document).ready(init);
