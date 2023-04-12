const Tickets = {
    components: {
        'issues-table': IssuesTable,
        'engagement-aside': EngagementsListAside,
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
            engagements.push({id: null, name:'All engagements'})
            $(this.engagementsTableId).bootstrapTable('append', engagements);
            this.engagements = engagements
            this.setEngagementEvent(data['items'])
            this.engagementCount = data['total'];
            if (data['total'] > 0) {
                this.selectFirstEngagement();
            }
            return data['items']
        })
    },
    methods: {
        setEngagementEvent(engagementList) {
            const vm = this;
            $('#engagement-table').on('click', 'tbody tr:not(.no-records-found)', function(event) {
                const selectedUniqId = parseInt(this.getAttribute('data-uniqueid'));
                vm.selectedEngagement = engagementList.find(row => row.id === selectedUniqId);
                $(this).addClass('highlight').siblings().removeClass('highlight');
            });
        },
        async fetchEngagements() {
            const res = await fetch (`/api/v1/engagements/engagements/${getSelectedProjectId()}`,{
                method: 'GET',
            })
            return res.json();
        },
        selectFirstEngagement() {
            const vm = this;
            $('#engagement-table tbody tr').each(function(i, item) {
                if(i === 0) {
                    const firstRow = $(item);
                    firstRow.addClass('highlight');
                    vm.selectedEngagementRowIndex = 0;
                    vm.selectedEngagement = $('#engagement-table').bootstrapTable('getData')[0];
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
            >
            </engagement-aside>
            <issues-table 
                :engagement="selectedEngagement">
            </issues-table>
        </main>
    `
};

register_component('tickets', Tickets);


