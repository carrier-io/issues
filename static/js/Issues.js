const Tickets = {
    components: {
        'issues-table': IssuesTable,
        'engagement-aside': EngagementsListAside,
        'engagement-card': TopEngagementCard,
    },
    data() {
        return {
            engagementsTableId: "#engagement-table",
            engagements: [],
            selectedEngagement: {
                name: null,
            },
            selectedEngagementRowIndex: null,
            engagementCount: 0,
        }
    },
    mounted() {
        const vm = this;
        this.fetchEngagements().then(data => {
            engagements = data['items']
            engagements.unshift({id: -1, name:'All engagements'})
            $(this.engagementsTableId).bootstrapTable('append', engagements);
            this.engagements = engagements
            this.setEngagementEvent(engagements)
            this.engagementCount = data['total'];
            if (data['total'] > 0) {
                this.selectEngagement(0);
            }
            return engagements
        })
    },
    methods: {
        refreshEngagements(){
            currentEngIndex = this.selectedEngagementRowIndex
            this.fetchEngagements().then(data => {
                $(this.engagementsTableId).bootstrapTable("removeAll")
                engagements = data['items']
                engagements.unshift({id: -1, name:'All engagements'})
                $(this.engagementsTableId).bootstrapTable('append', engagements);
                this.engagements = engagements
                this.setEngagementEvent(engagements)
                this.engagementCount = data['total'];
                if (data['total'] > currentEngIndex) {
                    this.selectEngagement(currentEngIndex);
                }
                return engagements
            })
        },

        setEngagementEvent(engagementList) {
            const vm = this;
            $('#engagement-table').on('click', 'tbody tr:not(.no-records-found)', function(event) {
                const selectedUniqId = parseInt(this.getAttribute('data-uniqueid'));
                for (let i=0; i<engagementList.length; i++){
                    eng = engagementList[i]
                    if (eng.id === selectedUniqId){
                        vm.selectedEngagement = eng
                        vm.selectedEngagementRowIndex = i
                    }
                }
                $(this).addClass('highlight').siblings().removeClass('highlight');
            });
        },
        async fetchEngagements() {
            const res = await fetch (`/api/v1/engagements/engagements/${getSelectedProjectId()}`,{
                method: 'GET',
            })
            return res.json();
        },
        selectEngagement(index) {
            const vm = this;
            $('#engagement-table tbody tr').each(function(i, item) {
                if(i === index) {
                    const firstRow = $(item);
                    firstRow.addClass('highlight');
                    vm.selectedEngagementRowIndex = index;
                    vm.selectedEngagement = $('#engagement-table').bootstrapTable('getData')[index];
                }
            })
        },
    },
    template: ` 
        <main class="d-flex align-items-start justify-content-center mb-3">
            <engagement-aside
                :engagement-count="engagementCount"
                :selected-engagement="selectedEngagement"
                :selected-engagement-row-index="selectedEngagementRowIndex"
                @engagementAdded="refreshEngagements"
            >
            </engagement-aside>
            <div class="w-100 mr-3">
                <div v-if="selectedEngagement.id!=-1">
                    <engagement-card
                        :engagement="selectedEngagement"
                    >
                    </engagement-card>
                </div>
                <div>
                    <issues-table 
                        :engagement="selectedEngagement"
                        :engagementList="engagements">
                    </issues-table>
                </div>
            </div>
        </main>
    `
};

register_component('tickets', Tickets);


