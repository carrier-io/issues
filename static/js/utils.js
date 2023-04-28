function titleFormatter(value){
  charLimit = 40
  if (value.length > charLimit){
    return value.slice(0, charLimit) + '...'
  }
  return value
}

window.tagsEvents = {
  "click .wraped-tag": function (e, value, row, index) {
    $('#issues-table').bootstrapTable('updateCell', {
      index: index,
      field: "tags",
      value: {'expand': true, tags: value}
    })
  }
}

TagsFormatter = {
  stringToColour(str) {
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    var colour = '#';
    for (var i = 0; i < 3; i++) {
      var value = (hash >> (i * 8)) & 0xFF;
      colour += ('00' + value.toString(16)).substr(-2);
    }
    return colour;
  },

  getTagColor(tag){
    colorsMap = new Map()
    colorsMap.set(0, '--success')
    colorsMap.set(1, '--green')
    colorsMap.set(2, '--error')
    colorsMap.set(3, '--magenta')
    colorsMap.set(4, '--blue')
    colorsMap.set(5, '--purple')
    colorsMap.set(6, '--yellow')
    colorsMap.set(7, '--info')
    colorsMap.set(8, '--basic')
    colorsCount = colorsMap.size
    return colorsMap.get(tag.length%colorsCount)
  },

  expandedFormat(tags){
    txt = ``
    tags.forEach(tag => {
      color = this.getTagColor(tag.tag)
      txt += `<button class="btn btn-xs btn-painted rounded-pill mr-2"
          style="--text-color: var(${color}); --brd-color: var(${color})" value="${tag.id}">${tag.tag}
        </button>`
    })
    return txt
  },

  wrappedFormat(tags){
    if (tags.length==0)
      return ''

    value = tags[0].tag
    color = this.getTagColor(value)
    txt = `<button class="btn btn-xs btn-painted rounded-pill mr-2" 
          style="--text-color: var(${color}); --brd-color: var(${color})">${value}
          </button>`
    
    txt += `<button class="wraped-tag btn btn-xs btn-painted rounded-pill mr-2" 
          style="--text-color: var(--gray600); --brd-color: var(--gray600)">
            + ${tags.length-1}
          </button>`
    return txt
  },
  
  format(tags){
    if (tags['expand'])
      return TagsFormatter.expandedFormat(tags.tags)
    if (tags.length==2)
      return TagsFormatter.expandedFormat(tags)
    return TagsFormatter.wrappedFormat(tags)
  }
}

function actionsFormatter(value, row, index) {
  result = [
    '<a class="issue-delete ml-2" href="javascript:void(0)" title="Delete">',
    '<i class="icon__18x18 icon-delete"></i>',
    '</a>',
  ].join('')
  return result
}

window.actionsEvents = {
  "click .issue-delete": function (e, value, row, index) {
    axios.delete(issue_detail_url + row.id)
      .then(function () {
        $("#issues-table").bootstrapTable("refresh");
        showNotify("SUCCESS", "Successfully deleted")
      })
      .catch(function (error) {
        showNotify("ERROR", error.response.data['error'])
      });
  }
}

function getNestedValue(fieldStr, object){
  fields = fieldStr.split('.')
  for (let i=0; i<fields.length; i++){
    object = object[fields[i]]
  }
  return object
}

function setOptions(selectId='#input-engagement', engagement=null){
  engs = vueVm.registered_components.engagement_container.engagements
  engs = JSON.parse(JSON.stringify(engs))
  engs[0]['name'] = "Select"
  tagText = ``
  engs.forEach(eng => {
    selected = eng.hash_id == engagement ? "selected" : "" 
    tagText += `<option value="${eng.hash_id}" ${selected}>${eng.name}</option>`
  });
  $(selectId).append(tagText)
  $(selectId).selectpicker('refresh')
  $(selectId).selectpicker('render')
}

function clearOptions(selectId='#input-engagement'){
  $(selectId).empty()
  $(selectId).selectpicker('refresh')
  $(selectId).selectpicker('render')
}


