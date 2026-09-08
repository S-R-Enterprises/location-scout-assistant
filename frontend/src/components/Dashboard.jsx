import React from 'react'
import SummaryCards from './SummaryCards'
import SceneTable from './SceneTable'
import ShootPlan from './ShootPlan'
import MapView from './MapView'
import Warnings from './Warnings'

export default function Dashboard({ report }) {
  return (
    <div className="space-y-8">
      <SummaryCards report={report} />
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2">
          <SceneTable scenesLocations={report.scenes_locations} />
        </div>
        <div>
          <MapView
            shootOrder={report.shoot_order}
            scenesLocations={report.scenes_locations}
          />
        </div>
      </div>
      <ShootPlan shootOrder={report.shoot_order} logistics={report.logistics} />
      <Warnings warnings={report.warnings} />
    </div>
  )
}
