$("#modal-view").on("show.bs.modal", (e) => {
  var row = $("#table").bootstrapTable("getRowByUniqueId", view_row_id);
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


function actionsFormatter(value, row, index) {
  result = [
    '<a class="issue-view" href="javascript:void(0)" title="View">',
    '<i class="fa fa-eye" style="color: #858796"></i>',
    '</a>',
  ].join('')

  if (row.type == "Activity"){
    result += '<a class="issue-edit ml-2" href="javascript:void(0)" title="Edit">'
    result += '<i class="fa-regular fa-pen-to-square" style="color: #858796"></i>'
    result += '</a>'
    result += '<a class="issue-delete ml-2" href="javascript:void(0)" title="Delete">'
    result += '<i class="fa fa-trash" style="color: #858796"></i>'
    result += '</a>'
  }
  return result
}

window.actionsEvents = {
  "click .issue-view": async (e, value, row, index) => {
    console.log(issue_detail_url)
    try{
      const resp = await axios.get(issue_detail_url+row.id)
      data = resp.data['item']
    }catch (error){
      console.log(error)
    }
    console.log(data['snapshot']['title'])
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
        $("#table").bootstrapTable("remove", {
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
  }
}


function getNestedValue(fieldStr, object){
  fields = fieldStr.split('.')
  for (let i=0; i<fields.length; i++){
    object = object[fields[i]]
  }
  return object
}


$(document).on('vue_init', () => {

  $("#modal-create").on("show.bs.modal", function (e) {
    $("#form-create").get(0).reset();
  });

  $('#refreshTable').click(function() {
    $('#table').bootstrapTable('refresh');
  });


  $("#save").click(function() {
    var data = $("#form-create").serializeObject();
    data['type'] = "Activity"

    axios.post(issues_api_url, data)
      .then(function (response) {
        $("#modal-create").modal("hide");
        $("#table").bootstrapTable("refresh", {});
        showNotify("SUCCESS");
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
      $("#table").bootstrapTable("refresh", {});
    })
    .catch(error => {
      showNotify("ERROR", error.response.data['error'])
    })

  });


});

