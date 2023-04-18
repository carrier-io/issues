
const EngagementsListAside = {
    props: ['selectedEngagementRowIndex', 'selectedEngagement', 'engagementCount'],
    emits: ['engagementAdded'],
    data() {
        return {
            currentEngIndex: null,
        }
    },
    components: {
        'engagement-creation-modal': EngagementCreationModal,
    },
    computed: {
        responsiveTableHeight() {
            return `${(window.innerHeight - 286)}px`;
        }
    },
    methods: {
        addedHandler(){
            this.$emit('engagementAdded')
        },
    },
    template: `
        <aside class="m-3 card card-table-sm" style="width: 340px">
            <div class="row px-4 pt-4">
                <div class="col-8">
                    <h4>Engagements</h4>
                </div>
                <div class="col-4">
                    <div class="d-flex justify-content-end">
                        <engagement-creation-modal
                            @added="addedHandler"
                        >
                        </engagement-creation-modal>
                    </div>
                </div>
            </div>
            <hr class="hr mb-0" />
            <div class="card-body" style="padding-top: 0">
                <table class="table table-borderless table-fix-thead"
                    id="engagement-table"
                    data-toggle="table"
                    data-show-header="false"
                    data-unique-id="id">
                    <thead class="thead-light bg-transparent">
                        <tr>
                            <th data-visible="false" data-field="id">index</th>
                            <th data-formatter="nameFormatter" data-field="name" class="engagement-name">NAME</th>
                        </tr>
                    </thead>
                    <tbody :style="{'height': responsiveTableHeight}">
                    </tbody>
                </table>
                <div class="p-3">
                    <span class="font-h5 text-gray-600">{{ engagementCount }} items</span>
                </div>
            </div>
        </aside>
    `
}

function nameFormatter(value, row){
    allEngagement = row['id'] == -1
    if(allEngagement){
        return value
    }
    txt = `<div class="pl-2"><img class="mr-2" src="/issues/static/ico/circle.svg">${value}</div>`
    return txt
}