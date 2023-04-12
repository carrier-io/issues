$("#modal-view").on("show.bs.modal", (e) => {
  var row = $("#issues-table").bootstrapTable("getRowByUniqueId", view_row_id);
  $("#form-view").get(0).reset();
  // $("#view-data").val(JSON.stringify(row));
  //
  $("#view-title").val(row.snapshot.title);
  $("#view-description").val(row.snapshot.description);
  $("#view-severity").val(row.severity);
  $("#view-type").val(row.type);
  $("#view-project").val(row.project);
  $("#view-asset").val(row.asset);
  $("#view-status").val(row.status);
  $("#view-state").val(row.state.value);
  $("#view-tags").val(row.tags.join(", "));
  //
  if (row.jira != null) {
    $("#view-jira").val(row.jira.server + ":" + row.jira.ticket);
  }
  //
  $("#view-logs").val(row.log.join("\n"));
});

function titleFormatter(value){
  charLimit = 40
  if (value.length > charLimit){
    return value.slice(0, charLimit) + '...'
  }
  return value
}

var stringToColour = function(str) {
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
}

function tagsFormatter(tags){
  txt = ``
  tags.forEach(tag => {
    color = stringToColour(tag.tag)
    txt += `<button class="tag btn btn-xs btn-painted rounded-pill mr-2"
        style="--text-color: ${color}; --brd-color: ${color}" value="${tag.id}">${tag.tag}
      </button>`
  })
  return txt
}

function actionsFormatter(value, row, index) {
  result = [
    '<a class="issue-delete ml-2" href="javascript:void(0)" title="Delete">',
    '<i class="fa fa-trash" style="color: #858796"></i>',
    '</a>',
  ].join('')
  return result
}

window.tagsEvents = {
  "click .tag": function(e, value, row, index){
    tagId = parseInt(e.currentTarget.value)
    url = $("#issues-table").data('url')
    value = JSON.stringify(value)
    $("#issues-table").bootstrapTable('refresh', {
      url: url + "?tags=" + tagId
    })
  }
}


window.actionsEvents = {
  "click .issue-view": async (e, value, row, index) => {
    try{
      const resp = await axios.get(issue_detail_url+row.id)
      data = resp.data['item']
    }catch (error){
      console.log(error)
    }
    $("#view-title").val(data['snapshot']['title'])
    $("#view-description").val(data['snapshot']['description'])
    $("#view-severity").val(data['severity'])
    $("#view-status").val(data['status'])
    $("#view-type").val(data['type'])
    $("#view-asset").val(data['asset'])
    $("#view-project").val(data['project'])
    $("#view-state").val(data['state']['value'])
    $("#view-jira").val(data['jira'])
    $("#view-logs").val(data['logs'].toString())
    $("#view-tags").val(data['tags'].toString())
    // $("#view-comments").val(data['comments'].toString())
    $("#modal-view").modal("show");
  },
  
  "click .issue-delete": function (e, value, row, index) {
    axios.delete(issue_detail_url + row.hash_id)
      .then(function () {
        $("#issues-table").bootstrapTable("remove", {
          field: "id",
          values: [row.id]
        });
        showNotify("SUCCESS", "Successfully deleted")
      })
      .catch(function (error) {
        showNotify("ERROR", error.response.data['error'])
      });
  },
  
  "click .issue-edit": function (e, value, row, index) {
    $("#modal-edit").modal("show");
    $("#edit").attr('issue-id', row.hash_id)
    $.each($("form#form-edit .form-control"), (ind, tag)  => {
      tag.value = getNestedValue(tag.name, row)
    })
  },
}


function getNestedValue(fieldStr, object){
  fields = fieldStr.split('.')
  for (let i=0; i<fields.length; i++){
    object = object[fields[i]]
  }
  return object
}


function setEngagementsOptions(){
  engs = vueVm.registered_components.tickets.engagements
  tagText = ``
  engs.forEach(eng => {
    tagText += `<option value="${eng.hash_id}">${eng.name}</option>`
  });
  $('#input-engagement').append(tagText)
  $('#input-engagement').selectpicker('refresh')
  $('#input-engagement').selectpicker('render')
}

function clearEngagementsOptions(){
  $('#input-engagement').empty()
  $('#input-engagement').selectpicker('refresh')
  $('#input-engagement').selectpicker('render')
}

function uploadAttachments(issueId){
  var formData = new FormData();
  var files = $("#dropInput")[0].files
  
  // return if no file has been selected
  if (files.length==0) return

  for (let i=0; i<files.length; i++){
      formData.append("files[]", files[i])
  }

  axios.post(attachmentsUrl+issueId, payload=formData)
      .then(() => {
          $("#dropInput").val(null);
          $("#previewArea").empty()
      })
      .catch((error)=>{
        showNotify("ERROR", "Attachment uploading failed")
      })
}


$(document).on('vue_init', () => {

  $("#modal-create").on("show.bs.modal", function (e) {
    $("#form-create").get(0).reset();
    $('#input-engagement').append('jdsajdksajdkadjk')
    setEngagementsOptions()
  });
  $("#modal-create").on("hidden.bs.modal", function(){
    clearEngagementsOptions()
    $("#textarea-description").summernote('reset')
  });

  $('#refreshTable').click(function() {
    $('#issues-table').bootstrapTable('refresh');
  });

  $("#save").click(function() {
    var data = $("#form-create").serializeObject();
    data['description'] = $("#textarea-description").summernote('code')
    data['tags'] = data['tags'].split(',')
    
    axios.post(issues_api_url, data)
      .then(response => {
        issueId = response.data['item']['id']
        uploadAttachments(issueId)
        $("#modal-create").modal("hide");
        $("#issues-table").bootstrapTable("refresh", {});
        showNotify("SUCCESS", "Ticket created");
      })
      .catch(function (error) {
        console.log(error);
      });
    

  });

  $("#edit").click(function(){
    data = {}
    $.each($("form#form-edit .form-control"),  (ind, tag)  => {
      data[tag.name] = tag.value
    })
    data['severity'] = $("#edit-severity").val()
    data['snapshot.severity'] = $("#edit-severity").val()
    data['asset'] = data['snapshot.asset']
    data['scan_project'] = data['snapshot.project']
    id =  $("#edit").attr('issue-id')
    axios.put(issue_detail_url + id, data)
    .then(() => {
      showNotify("SUCCESS", "Successfully updated")
      $("#modal-edit").modal('hide')
      $("#issues-table").bootstrapTable("refresh", {});
    })
    .catch(error => {
      showNotify("ERROR", error.response.data['error'])
    })

  });

  $('#textarea-description').summernote({
    height: 150,                 // set editor height
    minHeight: null,             // set minimum height of editor
    maxHeight: null,             // set maximum height of editor
    focus: true,                  // set focus to editable area after initializing summernote
  });

});

