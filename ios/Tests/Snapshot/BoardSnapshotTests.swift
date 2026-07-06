import XCTest
import SwiftUI
import SnapshotTesting
@testable import LevelFeature
import GameContent
import Simulation

/// Снапшоты доски: для КАЖДОЙ полностью-заполненной расстановки (все сцены по панелям × все
/// размещения героев) рендерим `LevelBoardView` в PNG. Список расстановок и имена (с статусом
/// SOLVED/wrong и «кто где») — из tools/gen_arrangements.py → GeneratedArrangements.swift.
/// Первый прогон с record: .all генерит эталоны в Tests/Snapshot/__Snapshots__/.
final class BoardSnapshotTests: XCTestCase {

    private let size = CGSize(width: 844, height: 390)   // ландшафт (iPhone)

    override func setUp() {
        super.setUp()
        UIView.setAnimationsEnabled(false)
    }

    func testArrangements() throws {
        let pack = try RomeContent.load()
        let byLevel = Dictionary(grouping: GeneratedArrangements.all, by: { $0.level })
        withSnapshotTesting(record: .all) {
            for (levelId, cases) in byLevel.sorted(by: { $0.key < $1.key }) {
                guard let level = pack.levels.first(where: { $0.id == levelId }) else {
                    XCTFail("level '\(levelId)' not found"); continue
                }
                for c in cases {
                    let view = LevelBoardView(level: level, db: pack.db, debugArrangement: c.panels)
                        .frame(width: size.width, height: size.height)
                    assertSnapshot(of: view,
                                   as: .image(layout: .fixed(width: size.width, height: size.height)),
                                   named: c.name, testName: levelId)
                }
            }
        }
    }
}
