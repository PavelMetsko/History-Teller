using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

namespace HistoryTeller.Game
{
    /// <summary>
    /// Фишка дока: перетаскивание с гостом за пальцем (drop на панель)
    /// + tap-выбор как фолбэк (тап по фишке, потом тап по панели).
    /// </summary>
    public sealed class ChipDrag : MonoBehaviour,
        IBeginDragHandler, IDragHandler, IEndDragHandler, IPointerClickHandler
    {
        private GameController _owner;
        private string _kind; // "scene" | "char"
        private string _id;
        private Transform _ghost;

        public void Init(GameController owner, string kind, string id)
        {
            _owner = owner;
            _kind = kind;
            _id = id;
        }

        public void OnBeginDrag(PointerEventData e)
        {
            _ghost = _owner.CreateGhost(_kind, _id);
            MoveGhost(e);
        }

        public void OnDrag(PointerEventData e) => MoveGhost(e);

        private void MoveGhost(PointerEventData e)
        {
            if (_ghost != null) _ghost.position = e.position; // ScreenSpaceOverlay
        }

        public void OnEndDrag(PointerEventData e)
        {
            if (_ghost != null)
            {
                Destroy(_ghost.gameObject);
                _ghost = null;
            }
            var results = new List<RaycastResult>();
            EventSystem.current.RaycastAll(e, results);
            foreach (var r in results)
            {
                var pm = r.gameObject.GetComponentInParent<PanelMarker>();
                if (pm != null)
                {
                    _owner.DropOnPanel(pm.Index, _kind, _id);
                    return;
                }
            }
        }

        public void OnPointerClick(PointerEventData e)
        {
            if (e.dragging) return;
            _owner.ChipTapped(_kind, _id);
        }
    }
}
